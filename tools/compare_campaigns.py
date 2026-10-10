"""Compare deux campagnes (typiquement simulation vs vrai capteur) sur les mêmes graphiques.

    python tools/compare_campaigns.py reports/<campagne_sil> reports/<campagne_hil>
    python tools/compare_campaigns.py A B --labels "Simulation" "Capteur réel" --out formation/08-simulation-vs-reel/resultats

Lit les fichiers results.json et les CSV bruts de chaque campagne, puis produit :
- comparaison.md : tableau des mesures clés côte à côte, avec l'écart ;
- des graphiques superposés : bruit (T03), linéarité (T04), FFT (T07), échelon (T08).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from processing import signal_tools as sp  # noqa: E402
from report.plots import BLUE, ORANGE, _save, plt  # noqa: E402

FS = 500.0


def load_csv(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def load_campaign(folder: Path) -> dict:
    data = json.loads((folder / "results.json").read_text(encoding="utf-8"))
    return {"meta": data["meta"], "results": {r["id"]: r for r in data["results"]}, "raw": folder / "raw"}


def key_table(a, b, labels) -> str:
    lines = [f"| Test | Mesure | {labels[0]} | {labels[1]} | Écart |", "|---|---|---|---|---|"]
    for tid in sorted(set(a["results"]) & set(b["results"])):
        ra, rb = a["results"][tid], b["results"][tid]
        for name, va in ra["measures"].items():
            vb = rb["measures"].get(name)
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                diff = f"{vb - va:+.4g}"
                lines.append(f"| {tid} | {name} | {va:.4g} | {vb:.4g} | {diff} |")
        lines.append(f"| {tid} | **verdict** | {ra['verdict']} | {rb['verdict']} | |")
    return "\n".join(lines)


def plot_noise(cams, labels, out):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
    for cam, label, color in zip(cams, labels, (BLUE, ORANGE)):
        f = cam["raw"] / "T03_repos.csv"
        if not f.exists():
            continue
        az = load_csv(f)["az"]
        a1.hist((az - az.mean()) * 1000, bins=50, alpha=0.55, color=color, label=label)
        freqs, amp = sp.spectrum(az, FS)
        a2.semilogy(freqs[1:], amp[1:] * 1000, lw=0.7, color=color, label=label)
    a1.set_xlabel("bruit sur Z (mg)")
    a1.set_title("Distribution du bruit")
    a1.legend()
    a2.set_xlabel("fréquence (Hz)")
    a2.set_ylabel("amplitude (mg)")
    a2.set_title("Spectre du bruit")
    a2.legend()
    fig.suptitle(f"T03 · Bruit au repos : {labels[0]} et {labels[1]}", fontweight="bold")
    return _save(fig, out / "compare_T03.png")


def plot_linearity(cams, labels, out):
    fig, ax = plt.subplots(figsize=(8, 3.8))
    width = 3.5
    for i, (cam, label, color) in enumerate(zip(cams, labels, (BLUE, ORANGE))):
        files = sorted(cam["raw"].glob("T04_angle_*.csv"))
        if not files:
            continue
        angles = np.array([float(p.stem.split("_")[-1]) for p in files])
        measured = np.array([load_csv(p)["ax"].mean() for p in files])
        fit = sp.linear_fit(np.sin(np.radians(angles)), measured)
        ax.bar(angles + (i - 0.5) * width, fit.residuals * 1000, width,
               color=color, label=f"{label} · R² = {fit.r2:.5f}")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("angle (°)")
    ax.set_ylabel("écart à la droite ajustée (mg)")
    ax.set_title(f"T04 · Erreur de linéarité : {labels[0]} et {labels[1]}")
    ax.legend()
    return _save(fig, out / "compare_T04.png")


def plot_fft(cams, labels, out, freq=10):
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for cam, label, color in zip(cams, labels, (BLUE, ORANGE)):
        f = cam["raw"] / f"T07_vibration_{freq}Hz.csv"
        if not f.exists():
            continue
        env = sp.envelope(load_csv(f)["az"], FS)
        freqs, amp = sp.spectrum(env, FS)
        sel = freqs <= 60
        ax.plot(freqs[sel], amp[sel] * 1000, color=color, lw=1, label=label)
    ax.set_xlabel("fréquence (Hz)")
    ax.set_ylabel("amplitude de l'enveloppe (mg)")
    ax.set_title(f"T07 · FFT de l'enveloppe, vibreur modulé à {freq} Hz")
    ax.legend()
    return _save(fig, out / "compare_T07.png")


def plot_step(cams, labels, out):
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for cam, label, color in zip(cams, labels, (BLUE, ORANGE)):
        f = cam["raw"] / "T08_echelon.csv"
        if not f.exists():
            continue
        d = load_csv(f)
        t = (d["t_us"] - d["t_us"][0]) / 1e6
        k = len(t) // 10
        x = sp.butter_lowpass(d["ax"], FS, 20)
        norm = (x - x[:k].mean()) / (x[-len(x) // 5:].mean() - x[:k].mean())
        ax.plot((t - t[k]) * 1000, norm, color=color, lw=1.6, label=label)
    ax.axhspan(0.95, 1.05, color="#2e9e5b", alpha=0.15, label="bande ±5 %")
    ax.set_xlim(-100, 600)
    ax.set_xlabel("temps depuis l'ordre du servo (ms)")
    ax.set_ylabel("réponse normalisée")
    ax.set_title(f"T08 · Échelon 0° → 45° : {labels[0]} et {labels[1]}")
    ax.legend(loc="lower right")
    return _save(fig, out / "compare_T08.png")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("campaign_a", type=Path)
    p.add_argument("campaign_b", type=Path)
    p.add_argument("--labels", nargs=2, default=["Simulation", "Capteur réel"])
    p.add_argument("--out", type=Path, default=Path("formation/08-simulation-vs-reel/resultats"))
    args = p.parse_args()
    cams = [load_campaign(args.campaign_a), load_campaign(args.campaign_b)]
    args.out.mkdir(parents=True, exist_ok=True)
    table = key_table(*cams, args.labels)
    header = (f"# Comparaison : {args.labels[0]} ({cams[0]['meta']['run_id']}) "
              f"et {args.labels[1]} ({cams[1]['meta']['run_id']})\n\n")
    (args.out / "comparaison.md").write_text(header + table + "\n", encoding="utf-8")
    for fn in (plot_noise, plot_linearity, plot_fft, plot_step):
        print("graphique :", fn(cams, args.labels, args.out))
    print("tableau   :", args.out / "comparaison.md")


if __name__ == "__main__":
    main()
