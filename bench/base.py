"""Interface commune du banc : la même API pour le capteur simulé (SIL) et le vrai capteur (HIL).

Les procédures de test n'appellent que les méthodes définies ici. Elles ne savent donc pas
si elles parlent au simulateur ou à l'ESP32 : c'est ce qui permet de lancer exactement
les mêmes tests dans les deux modes.
"""
from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Caractéristiques du MPU6050 configuré en ±2 g (datasheet)
G_RANGE = 2.0          # pleine échelle en g
LSB_PER_G = 16384.0    # sensibilité accéléromètre à ±2 g
LSB_PER_DPS = 131.0    # sensibilité gyroscope à ±250 °/s
WHO_AM_I_EXPECTED = 0x68

ANGLE_MIN, ANGLE_MAX = -80.0, 80.0   # débattement autorisé du servo (degrés)
READ_MAX = 4000                      # taille max d'une acquisition (mémoire ESP32)


class SensorError(RuntimeError):
    """Erreur côté banc : capteur absent, réponse invalide, délai dépassé..."""


@dataclass
class Measurement:
    """Une acquisition : un tableau numpy par voie, toutes de même longueur."""

    t_us: np.ndarray   # horodatage en microsecondes (horloge de l'ESP32)
    ax: np.ndarray     # accélération en g
    ay: np.ndarray
    az: np.ndarray
    gx: np.ndarray     # vitesse angulaire en °/s
    gy: np.ndarray
    gz: np.ndarray
    temp: np.ndarray   # température interne en °C

    COLUMNS = ("t_us", "ax", "ay", "az", "gx", "gy", "gz", "temp")

    @property
    def t(self) -> np.ndarray:
        """Temps en secondes depuis le début de l'acquisition."""
        return (self.t_us - self.t_us[0]) / 1e6

    def __len__(self) -> int:
        return len(self.t_us)

    def save_csv(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(self.COLUMNS)
            cols = [getattr(self, c) for c in self.COLUMNS]
            for row in zip(*cols):
                w.writerow([int(row[0])] + [f"{v:.6f}" for v in row[1:]])
        return path

    @classmethod
    def concat(cls, parts: list["Measurement"]) -> "Measurement":
        return cls(**{c: np.concatenate([getattr(p, c) for p in parts]) for c in cls.COLUMNS})


class SensorInterface(ABC):
    """Contrat commun. Les vérifications d'arguments sont faites ici, une seule fois."""

    mode: str = "?"
    serial_number: str = "?"
    firmware_version: str = "?"

    # --- API publique utilisée par les tests -------------------------------------------
    def identify(self) -> int:
        """Lit le registre WHO_AM_I du capteur (0x68 attendu)."""
        return self._identify()

    def set_angle(self, angle_deg: float) -> None:
        if not ANGLE_MIN <= angle_deg <= ANGLE_MAX:
            raise ValueError(f"Angle {angle_deg}° hors plage [{ANGLE_MIN}, {ANGLE_MAX}]")
        self._set_angle(float(angle_deg))

    def set_vibration(self, freq_hz: float) -> None:
        """Module le moteur vibreur en tout-ou-rien à freq_hz (0 = arrêt)."""
        if not 0 <= freq_hz <= 100:
            raise ValueError(f"Fréquence de vibration {freq_hz} Hz hors plage [0, 100]")
        self._set_vibration(float(freq_hz))

    def read(self, n: int) -> Measurement:
        self._check_n(n)
        return self._read(int(n))

    def step(self, angle_deg: float, n: int) -> Measurement:
        """Acquiert n mesures ; le servo reçoit l'ordre `angle_deg` à l'échantillon n // 10."""
        self._check_n(n)
        if not ANGLE_MIN <= angle_deg <= ANGLE_MAX:
            raise ValueError(f"Angle {angle_deg}° hors plage")
        return self._step(float(angle_deg), int(n))

    def wait(self, seconds: float) -> None:
        """Laisse le montage se stabiliser (servo, vibrations)."""
        self._wait(float(seconds))

    def raw_command(self, command: str) -> str:
        """Envoie une commande brute du protocole série (utilisé par le test de robustesse)."""
        return self._raw_command(command)

    @property
    @abstractmethod
    def sample_rate(self) -> float: ...

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # --- À implémenter par le simulateur et par le pilote réel --------------------------
    @staticmethod
    def _check_n(n: int) -> None:
        if not 1 <= n <= READ_MAX:
            raise ValueError(f"Nombre de mesures {n} hors plage [1, {READ_MAX}]")

    @abstractmethod
    def _identify(self) -> int: ...

    @abstractmethod
    def _set_angle(self, angle: float) -> None: ...

    @abstractmethod
    def _set_vibration(self, freq: float) -> None: ...

    @abstractmethod
    def _read(self, n: int) -> Measurement: ...

    @abstractmethod
    def _step(self, angle: float, n: int) -> Measurement: ...

    @abstractmethod
    def _wait(self, seconds: float) -> None: ...

    @abstractmethod
    def _raw_command(self, command: str) -> str: ...
