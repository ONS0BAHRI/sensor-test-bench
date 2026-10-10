"""Un graphique par test, enregistré en PNG pour le rapport HTML et le README."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

BLUE, ORANGE, GREY, RED, GREEN = "#2a6fdb", "#e8833a", "#8a8f98", "#d64545", "#2e9e5b"

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 130, "font.size": 10, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.3, "legend.frameon": False,
})


def _save(fig, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_T02(r, path):
    d = r.plot_data
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar(x - 0.18, d["raw_offset"] * 1000, 0.36, color=GREY, label="offset brut")
    ax.bar(x + 0.18, d["residual"] * 1000, 0.36, color=BLUE, label="après calibration")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x, ["X", "Y", "Z"])
    ax.set_ylabel("écart (mg)")
    ax.set_title("T02 · La calibration ramène l'offset à moins de 1 mg")
    ax.legend()
    return _save(fig, path)


def plot_T03(r, path):
    d = r.plot_data
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
    noise = (d["az"] - d["az"].mean()) * 1000
    a1.hist(noise, bins=50, color=BLUE, alpha=0.85)
    a1.set_xlabel("bruit sur Z (mg)")
    a1.set_ylabel("nombre d'échantillons")
    a1.set_title("Distribution du bruit au repos")
    a2.semilogy(d["freqs"][1:], d["amp"][1:] * 1000, color=BLUE, lw=0.8)
    a2.set_xlabel("fréquence (Hz)")
    a2.set_ylabel("amplitude (mg)")
    a2.set_title("Spectre du bruit (FFT)")
    fig.suptitle("T03 · Bruit au repos", fontweight="bold")
    return _save(fig, path)


def plot_T04(r, path):
    d = r.plot_data
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    xs = np.linspace(0, d["expected"].max(), 50)
    a1.plot(xs, d["gain"] * xs + d["offset"], color=GREY, lw=1, label="droite ajustée")
    a1.plot(d["expected"], d["measured"], "o", color=BLUE, label="mesures")
    a1.set_xlabel("accélération attendue g·sin(θ) (g)")
    a1.set_ylabel("accélération mesurée (g)")
    a1.set_title(f"Mesure vs attendu · R² = {r.measures['R²']:.5f}")
    a1.legend()
    a2.bar(d["angles"], d["residuals"] * 1000, width=5, color=BLUE)
    lim_mg = 2.0 / 100 * 2.0 * 1000
    a2.axhline(lim_mg, color=RED, ls="--", lw=1, label=f"limite ±{lim_mg:.0f} mg (2 % PE)")
    a2.axhline(-lim_mg, color=RED, ls="--", lw=1)
    a2.set_xlabel("angle (°)")
    a2.set_ylabel("écart à la droite (mg)")
    a2.set_title("Erreur de linéarité")
    a2.legend(loc="lower right")
    fig.suptitle("T04 · Linéarité de l'axe X", fontweight="bold")
    return _save(fig, path)


def plot_T05(r, path):
    d = r.plot_data
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ideal = np.sin(np.radians(d["angles"]))
    ax.plot(d["angles"], (d["up"] - ideal) * 1000, "o-", color=BLUE, label="montée")
    ax.plot(d["angles"], (d["down"] - ideal) * 1000, "s-", color=ORANGE, label="descente")
    ax.set_xlabel("angle commandé (°)")
    ax.set_ylabel("écart à g·sin(θ) (mg)")
    ax.set_title(f"T05 · Hystérésis : écart max {r.measures['écart max (mg)']:.1f} mg (jeu du servo)")
    ax.legend()
    return _save(fig, path)


def plot_T06(r, path):
    v = r.plot_data["values"]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.plot(np.arange(1, len(v) + 1), (v - v.mean()) * 1000, "o-", color=BLUE)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("cycle")
    ax.set_ylabel("écart à la moyenne (mg)")
    ax.set_title(f"T06 · Répétabilité sur {len(v)} cycles : σ = {r.measures['écart-type (mg)']:.2f} mg")
    return _save(fig, path)


def plot_T07(r, path):
    d = r.plot_data
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
    t, az, env = d["example"]
    sel = t < 0.5
    a1.plot(t[sel], az[sel], color=GREY, lw=0.6, label="accélération Z brute")
    a1.plot(t[sel], env[sel] + az.mean(), color=BLUE, lw=1.8, label="enveloppe")
    a1.set_xlabel("temps (s)")
    a1.set_ylabel("g")
    a1.set_title("Vibreur modulé à 10 Hz : signal et enveloppe")
    a1.legend(loc="lower right", ncol=2)
    colors = [BLUE, ORANGE, GREEN, RED]
    for (f, (freqs, amp)), c in zip(d["spectra"].items(), colors):
        sel = freqs <= 60
        a2.plot(freqs[sel], amp[sel] * 1000, color=c, lw=1, label=f"{f} Hz → {d['found'][f]:.2f} Hz")
    a2.set_xlabel("fréquence (Hz)")
    a2.set_ylabel("amplitude de l'enveloppe (mg)")
    a2.set_title("FFT de l'enveloppe : un pic par fréquence commandée")
    a2.legend()
    fig.suptitle("T07 · Réponse en fréquence", fontweight="bold")
    return _save(fig, path)


def plot_T08(r, path):
    d = r.plot_data
    t_ms = (d["t"] - d["t_step"]) * 1000
    amp = d["final"] - d["initial"]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(t_ms, d["raw"], color=GREY, lw=0.6, label="brut")
    ax.plot(t_ms, d["filtered"], color=BLUE, lw=1.8, label="filtré 20 Hz")
    ax.axhspan(d["final"] - d["tol"] * amp, d["final"] + d["tol"] * amp, color=GREEN, alpha=0.15,
               label=f"bande ±{d['tol'] * 100:.0f} %")
    ax.axvline(0, color="black", lw=0.8, ls=":")
    ax.axvline(d["settle"] * 1000, color=RED, lw=1, ls="--",
               label=f"établi en {d['settle'] * 1000:.0f} ms")
    ax.set_xlabel("temps depuis l'ordre du servo (ms)")
    ax.set_ylabel("accélération X (g)")
    ax.set_title("T08 · Réponse à un échelon de 0° à 45°")
    ax.legend(loc="lower right")
    return _save(fig, path)


def plot_T09(r, path):
    d = r.plot_data
    sel = d["t"] < 1.0
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(d["t"][sel], d["raw"][sel] * 1000, color=GREY, lw=0.7, label="brut")
    ax.plot(d["t"][sel], d["filtered"][sel] * 1000, color=BLUE, lw=2, label=f"Butterworth {d['fc']} Hz")
    ax.set_xlabel("temps (s)")
    ax.set_ylabel("accélération X (mg)")
    ax.set_title(f"T09 · Le filtre retire {r.measures['réduction du bruit (%)']:.0f} % du bruit sans décaler le niveau")
    ax.legend()
    return _save(fig, path)


def plot_T10(r, path):
    dt = r.plot_data["dt_us"]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.hist(dt, bins=40, color=BLUE, alpha=0.85)
    ax.set_xlabel("période entre deux mesures (µs)")
    ax.set_ylabel("nombre")
    ax.set_title(f"T10 · Fréquence mesurée {r.measures['fréquence mesurée (Hz)']:.2f} Hz, "
                 f"gigue {r.measures['gigue (%)']:.2f} %")
    return _save(fig, path)


def plot_T13(r, path):
    d = r.plot_data
    names = list(d["signals"].keys())
    fig, axes = plt.subplots(2, 3, figsize=(11, 5.2), sharex=True)
    for ax, name in zip(axes.flat, names):
        y = d["signals"][name] * 1000
        status = "référence" if name == "sain" else r.measures[f"défaut {name}"]
        color = GREY if name == "sain" else (GREEN if status == "détecté" else RED)
        ax.plot(d["t"], y, color=color, lw=0.7)
        ax.set_title(f"{name} · {status}", color=color if name != "sain" else "black")
        ax.set_ylabel("mg")
    for ax in axes[-1]:
        ax.set_xlabel("temps (s)")
    fig.suptitle("T13 · Chaque défaut injecté est détecté, le signal sain ne déclenche rien",
                 fontweight="bold")
    return _save(fig, path)


PLOTTERS = {"T02": plot_T02, "T03": plot_T03, "T04": plot_T04, "T05": plot_T05, "T06": plot_T06,
            "T07": plot_T07, "T08": plot_T08, "T09": plot_T09, "T10": plot_T10, "T13": plot_T13}


def plot_result(result, outdir: Path) -> Path | None:
    fn = PLOTTERS.get(result.test_id)
    if fn is None:
        return None
    outdir.mkdir(parents=True, exist_ok=True)
    return fn(result, outdir / f"{result.test_id}.png")
