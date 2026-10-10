"""Faux ESP32 : rejoue le protocole série du firmware en s'appuyant sur le simulateur.

Permet de tester le pilote RealSensor (envoi des commandes, décodage des trames,
conversion des valeurs brutes, gestion des ERR) sans aucun matériel.
"""
from collections import deque

import numpy as np

from bench.base import LSB_PER_DPS, LSB_PER_G
from bench.simulated_sensor import SimulatedSensor


class FakeSerial:
    def __init__(self, port, baudrate=921600, timeout=5.0, disconnected=False):
        self.sim = SimulatedSensor(seed=7)
        self.disconnected = disconnected
        self.out = deque()
        self.closed = False

    # --- API pyserial utilisée par RealSensor ------------------------------------------
    def write(self, data: bytes):
        for line in data.decode("ascii").splitlines():
            self._handle(line.strip())

    def readline(self) -> bytes:
        return (self.out.popleft() + "\n").encode() if self.out else b""

    def reset_input_buffer(self):
        self.out.clear()

    def close(self):
        self.closed = True

    # --- copie du comportement du firmware ----------------------------------------------
    def _reply(self, text):
        self.out.append(text)

    def _handle(self, line):
        parts = line.split()
        cmd, args = parts[0], parts[1:]
        if cmd == "ID?":
            self._reply("ERR capteur absent sur le bus I2C" if self.disconnected else "ID 0x68")
        elif cmd == "FS?":
            self._reply("FS 500")
        elif cmd == "VER?":
            self._reply("VER 1.0.0")
        elif cmd == "SERVO":
            a = float(args[0])
            if not -80 <= a <= 80:
                return self._reply("ERR angle hors plage [-80, 80]")
            self.sim.set_angle(a)
            self._reply("OK")
        elif cmd == "VIB":
            self.sim.set_vibration(float(args[0]))
            self._reply("OK")
        elif cmd in ("READ", "STEP"):
            if self.disconnected:
                return self._reply("ERR lecture I2C impossible")
            if cmd == "READ":
                m = self.sim.read(int(args[0]))
            else:
                m = self.sim.step(float(args[0]), int(args[1]))
            self._send_block(m)
        else:
            self._reply(f"ERR commande inconnue: {cmd}")

    def _send_block(self, m):
        n = len(m)
        to_int = lambda x, k: np.round(x * k).astype(int)  # noqa: E731
        cols = [m.t_us, to_int(m.ax, LSB_PER_G), to_int(m.ay, LSB_PER_G), to_int(m.az, LSB_PER_G),
                to_int(m.gx, LSB_PER_DPS), to_int(m.gy, LSB_PER_DPS), to_int(m.gz, LSB_PER_DPS),
                np.round((m.temp - 36.53) * 340).astype(int)]
        self._reply(f"DATA {n}")
        for row in zip(*cols):
            self._reply(",".join(str(int(v)) for v in row))
        self._reply("END")
