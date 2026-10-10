"""Simulateur physique du banc : MPU6050 monté sur un servo SG90, avec un moteur vibreur.

Le modèle reproduit les imperfections réelles qu'un banc de test doit détecter :
- offset et erreur de gain par axe (ordres de grandeur de la datasheet MPU6050) ;
- bruit blanc gaussien et quantification sur 16 bits (1 LSB = 1/16384 g) ;
- servo à vitesse limitée (0,1 s pour 60°), jeu mécanique (hystérésis) et erreur de position ;
- moteur vibreur : porteuse ~170 Hz modulée en tout-ou-rien à la fréquence commandée,
  avec un temps de montée du moteur ;
- gigue de l'horodatage, légère dérive de température.
"""
from __future__ import annotations

import numpy as np

from .base import (G_RANGE, LSB_PER_G, WHO_AM_I_EXPECTED, Measurement, SensorError,
                   SensorInterface)


class SimulatedSensor(SensorInterface):
    mode = "sil"
    firmware_version = "simulateur-1.0"

    def __init__(
        self,
        fs: float = 500.0,
        seed: int = 42,
        offset_g: tuple[float, float, float] = (0.035, -0.020, 0.060),
        gain: tuple[float, float, float] = (1.020, 1.000, 0.985),
        noise_std_g: float = 0.004,
        gyro_noise_dps: float = 0.05,
        servo_speed_dps: float = 600.0,   # SG90 : 0,1 s / 60°
        backlash_deg: float = 0.4,        # jeu mécanique du servo
        servo_error_deg: float = 0.3,     # erreur de positionnement répétable
        vib_carrier_hz: float = 170.0,    # rotation du moteur vibreur
        vib_amp_g: float = 0.15,
        vib_tau_s: float = 0.015,         # temps de montée du moteur
        temp_c: float = 27.0,
        disconnected: bool = False,
        serial_number: str = "SIM-0001",
    ):
        self._fs = fs
        self.rng = np.random.default_rng(seed)
        self.offset = np.array(offset_g)
        self.gain = np.array(gain)
        self.noise_std = noise_std_g
        self.gyro_noise = gyro_noise_dps
        self.servo_speed = servo_speed_dps
        self.backlash = backlash_deg
        self.servo_error = servo_error_deg
        self.vib_carrier = vib_carrier_hz
        self.vib_amp = vib_amp_g
        self.vib_tau = vib_tau_s
        self.temp_c = temp_c
        self.disconnected = disconnected
        self.serial_number = serial_number

        self._cmd = 0.0        # angle commandé
        self._angle = 0.0      # angle réel du bras
        self._dir = 0          # sens du dernier mouvement (pour le jeu)
        self._vib = 0.0        # fréquence de modulation du vibreur
        self._env = 0.0        # enveloppe réelle du moteur (0..1)
        self._t = 0.0          # temps simulé (s)

    # -------------------------------------------------------------------------------------
    @property
    def sample_rate(self) -> float:
        return self._fs

    def _guard(self) -> None:
        if self.disconnected:
            raise SensorError("Capteur non détecté sur le bus I2C (simulation de câble débranché)")

    def _identify(self) -> int:
        self._guard()
        return WHO_AM_I_EXPECTED

    def _set_angle(self, angle: float) -> None:
        self._guard()
        if angle > self._cmd:
            self._dir = 1
        elif angle < self._cmd:
            self._dir = -1
        self._cmd = angle

    def _set_vibration(self, freq: float) -> None:
        self._guard()
        self._vib = freq

    def _wait(self, seconds: float) -> None:
        self._guard()
        self._advance(int(round(seconds * self._fs)), record=False)

    def _read(self, n: int) -> Measurement:
        self._guard()
        return self._advance(n, record=True)

    def _step(self, angle: float, n: int) -> Measurement:
        self._guard()
        k = n // 10
        before = self._advance(k, record=True)
        self._set_angle(angle)
        after = self._advance(n - k, record=True)
        return Measurement.concat([before, after])

    def _raw_command(self, command: str) -> str:
        self._guard()
        parts = command.strip().split()
        if not parts:
            raise SensorError("ERR commande vide")
        if parts[0] == "ID?":
            return f"ID 0x{self._identify():02X}"
        if parts[0] == "FS?":
            return f"FS {int(self._fs)}"
        raise SensorError(f"ERR commande inconnue: {parts[0]}")

    # -------------------------------------------------------------------------------------
    def _target_angle(self) -> float:
        """Position finale réelle du bras : commande + erreur répétable + jeu mécanique."""
        error = self.servo_error * np.sin(0.9 * self._cmd)
        return self._cmd + error - self._dir * self.backlash

    def _advance(self, n: int, record: bool) -> Measurement | None:
        dt = 1.0 / self._fs
        max_step = self.servo_speed * dt
        alpha = 1.0 - np.exp(-dt / self.vib_tau)
        target = self._target_angle()

        angle = np.empty(n)
        rate = np.empty(n)
        env = np.empty(n)
        t = self._t + dt * np.arange(n)
        for i in range(n):
            move = float(np.clip(target - self._angle, -max_step, max_step))
            self._angle += move
            angle[i] = self._angle
            rate[i] = move / dt
            on = 1.0 if self._vib > 0 and (t[i] * self._vib) % 1.0 < 0.5 else 0.0
            self._env += (on - self._env) * alpha
            env[i] = self._env
        self._t += n * dt
        if not record:
            return None

        rng = self.rng
        theta = np.radians(angle)
        vib = env * self.vib_amp * np.sin(2 * np.pi * self.vib_carrier * t)
        ax = self.gain[0] * np.sin(theta) + self.offset[0] + 0.5 * vib + rng.normal(0, self.noise_std, n)
        ay = self.offset[1] + 0.3 * vib + rng.normal(0, self.noise_std, n)
        az = self.gain[2] * np.cos(theta) + self.offset[2] + vib + rng.normal(0, self.noise_std, n)
        gx = -0.5 + rng.normal(0, self.gyro_noise, n)
        gy = rate + 0.8 + rng.normal(0, self.gyro_noise, n)
        gz = 0.3 + rng.normal(0, self.gyro_noise, n)
        temp = self.temp_c + 0.02 * t / 60 + rng.normal(0, 0.02, n)
        t_us = np.round(t * 1e6 + rng.normal(0, 15, n)).astype(np.int64)

        def quantize(x):
            return np.clip(np.round(x * LSB_PER_G), -32768, 32767) / LSB_PER_G

        return Measurement(t_us=t_us, ax=quantize(ax), ay=quantize(ay), az=quantize(az),
                           gx=gx, gy=gy, gz=gz, temp=temp)


__all__ = ["SimulatedSensor", "G_RANGE"]
