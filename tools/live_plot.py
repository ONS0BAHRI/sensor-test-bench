"""Affichage en direct des mesures, pratique pour filmer la démo.

    python tools/live_plot.py                      # simulateur
    python tools/live_plot.py --mode hil --port COM3

Le servo balaie 0° -> 60° -> 0°, puis le vibreur se met en marche : on voit l'accélération
suivre l'inclinaison, puis la vibration apparaître.
"""
import argparse
import sys
from collections import deque
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench import open_bench  # noqa: E402

SCENARIO = [0, 10, 20, 30, 40, 50, 60, 60, 40, 20, 0, 0, "vib", "vib", "vib", "vib", "stop"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", default="sil", choices=["sil", "hil"])
    p.add_argument("--port")
    args = p.parse_args()
    bench = open_bench(args.mode, args.port)
    block = 250                                   # 0,5 s par image à 500 Hz
    window = 3000
    ax_hist, az_hist = deque(maxlen=window), deque(maxlen=window)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    line_x, = ax.plot([], [], lw=1, label="accélération X (inclinaison)")
    line_z, = ax.plot([], [], lw=1, label="accélération Z")
    title = ax.set_title("")
    ax.set_xlim(0, window)
    ax.set_ylim(-0.3, 1.4)
    ax.set_ylabel("g")
    ax.legend(loc="upper right")

    def update(i):
        step = SCENARIO[i % len(SCENARIO)]
        if step == "vib":
            bench.set_vibration(10)
            label = "vibreur 10 Hz"
        elif step == "stop":
            bench.set_vibration(0)
            label = "vibreur arrêté"
        else:
            bench.set_angle(step)
            label = f"servo à {step}°"
        m = bench.read(block)
        ax_hist.extend(m.ax)
        az_hist.extend(m.az)
        line_x.set_data(range(len(ax_hist)), ax_hist)
        line_z.set_data(range(len(az_hist)), az_hist)
        title.set_text(f"Banc MPU6050 en direct ({args.mode.upper()}) · {label}")
        return line_x, line_z, title

    _anim = FuncAnimation(fig, update, interval=500, cache_frame_data=False)  # noqa: F841
    plt.show()
    bench.close()


if __name__ == "__main__":
    main()
