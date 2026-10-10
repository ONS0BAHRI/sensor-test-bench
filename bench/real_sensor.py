"""Pilote du vrai banc (mode HIL) : dialogue avec le firmware ESP32 par liaison série USB.

Protocole texte (une commande par ligne, voir firmware/sensor_bench/sensor_bench.ino) :

    ID?            -> ID 0x68
    FS?            -> FS 500
    VER?           -> VER 1.0.0
    SERVO <deg>    -> OK
    VIB <hz>       -> OK                (0 = arrêt)
    READ <n>       -> DATA <n>, puis n lignes "t_us,ax,ay,az,gx,gy,gz,temp" (valeurs brutes), puis END
    STEP <deg> <n> -> idem READ ; le servo bouge à l'échantillon n/10
    toute erreur   -> ERR <message>
"""
from __future__ import annotations

import time

import numpy as np

from .base import LSB_PER_DPS, LSB_PER_G, Measurement, SensorError, SensorInterface

try:
    import serial  # pyserial
except ImportError:  # le mode simulation fonctionne sans pyserial
    serial = None


class RealSensor(SensorInterface):
    mode = "hil"

    def __init__(self, port: str, baudrate: int = 921600, timeout_s: float = 5.0,
                 serial_number: str = "MPU-0001"):
        if serial is None:
            raise SensorError("pyserial n'est pas installé : pip install pyserial")
        try:
            self._ser = serial.Serial(port, baudrate, timeout=timeout_s)
        except serial.SerialException as exc:
            raise SensorError(f"Impossible d'ouvrir le port {port} : {exc}") from exc
        self.serial_number = serial_number
        time.sleep(2.0)                     # l'ESP32 redémarre à l'ouverture du port
        self._ser.reset_input_buffer()
        self.firmware_version = self._query("VER?").split()[-1]
        self._fs = float(self._query("FS?").split()[-1])

    # --- outils série ---------------------------------------------------------------------
    def _send(self, command: str) -> None:
        self._ser.write((command + "\n").encode("ascii"))

    def _readline(self) -> str:
        line = self._ser.readline().decode("ascii", errors="replace").strip()
        if not line:
            raise SensorError("Délai dépassé : pas de réponse de l'ESP32")
        if line.startswith("ERR"):
            raise SensorError(line)
        return line

    def _query(self, command: str) -> str:
        self._send(command)
        return self._readline()

    def _expect_ok(self, command: str) -> None:
        reply = self._query(command)
        if reply != "OK":
            raise SensorError(f"Réponse inattendue à '{command}' : {reply}")

    def _read_data_block(self, n: int) -> Measurement:
        header = self._readline()
        if header != f"DATA {n}":
            raise SensorError(f"En-tête inattendu : {header}")
        raw = np.empty((n, 8), dtype=np.int64)
        for i in range(n):
            fields = self._readline().split(",")
            if len(fields) != 8:
                raise SensorError(f"Ligne {i} invalide : {fields}")
            raw[i] = [int(v) for v in fields]
        if self._readline() != "END":
            raise SensorError("Fin de bloc END manquante")
        return Measurement(
            t_us=raw[:, 0],
            ax=raw[:, 1] / LSB_PER_G, ay=raw[:, 2] / LSB_PER_G, az=raw[:, 3] / LSB_PER_G,
            gx=raw[:, 4] / LSB_PER_DPS, gy=raw[:, 5] / LSB_PER_DPS, gz=raw[:, 6] / LSB_PER_DPS,
            temp=raw[:, 7] / 340.0 + 36.53,   # formule de la datasheet MPU6050
        )

    # --- implémentation de l'interface ------------------------------------------------------
    @property
    def sample_rate(self) -> float:
        return self._fs

    def _identify(self) -> int:
        return int(self._query("ID?").split()[-1], 16)

    def _set_angle(self, angle: float) -> None:
        self._expect_ok(f"SERVO {angle:.1f}")

    def _set_vibration(self, freq: float) -> None:
        self._expect_ok(f"VIB {freq:.2f}")

    def _read(self, n: int) -> Measurement:
        self._send(f"READ {n}")
        return self._read_data_block(n)

    def _step(self, angle: float, n: int) -> Measurement:
        self._send(f"STEP {angle:.1f} {n}")
        return self._read_data_block(n)

    def _wait(self, seconds: float) -> None:
        time.sleep(seconds)

    def _raw_command(self, command: str) -> str:
        return self._query(command)

    def close(self) -> None:
        try:
            self._send("VIB 0")
        finally:
            self._ser.close()
