"""Campagne de test complète en une seule commande (séquence type « fin de ligne »).

Exemples :
    python run_bench.py                               # simulation (SIL), capteur sain
    python run_bench.py --defective                   # simulation d'un capteur défectueux
    python run_bench.py --mode hil --port COM3        # vrai banc ESP32 + MPU6050
    python run_bench.py --mode hil --port /dev/ttyUSB0 --serial MPU-0002
    python run_bench.py --mode hil --port COM3 --docs   # range les graphiques dans les TP

Produit dans reports/<campagne>/ : données brutes CSV, graphiques PNG, results.json,
summary.md et un rapport HTML autonome. Chaque campagne est aussi ajoutée à reports/results.db.
Code de sortie : 0 si le capteur est conforme, 1 sinon (utilisable en intégration continue).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

from bench import open_bench
from bench.procedures import ALL_PROCEDURES, TestResult
from report.course import tp_image_path
from report.database import save_campaign
from report.html_report import write_html_report
from report.plots import plot_result

ROOT = Path(__file__).resolve().parent
GREEN, RED, BOLD, RESET = "\033[92m", "\033[91m", "\033[1m", "\033[0m"

# Capteur simulé volontairement hors tolérances : sert à montrer que le banc détecte un mauvais capteur.
DEFECTIVE_SENSOR = dict(offset_g=(0.21, -0.02, 0.06), noise_std_g=0.013, backlash_deg=1.6,
                        serial_number="SIM-DEFECT")


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "n/a"


def run_campaign(args) -> int:
    limits = yaml.safe_load((ROOT / args.limits).read_text(encoding="utf-8"))
    sensor_kwargs = {}
    if args.mode == "sil":
        sensor_kwargs = dict(DEFECTIVE_SENSOR) if args.defective else {}
        if args.serial and not args.defective:
            sensor_kwargs["serial_number"] = args.serial
        # Réglages du simulateur pour les exercices : chaque défaut peut être modifié séparément
        if args.noise is not None:
            sensor_kwargs["noise_std_g"] = args.noise
        if args.offset_x is not None:
            base = sensor_kwargs.get("offset_g", (0.035, -0.020, 0.060))
            sensor_kwargs["offset_g"] = (args.offset_x, base[1], base[2])
        if args.backlash is not None:
            sensor_kwargs["backlash_deg"] = args.backlash
        if args.seed is not None:
            sensor_kwargs["seed"] = args.seed
    elif args.serial:
        sensor_kwargs["serial_number"] = args.serial

    started = datetime.now()
    t0 = time.time()
    results: list[TestResult] = []
    with open_bench(args.mode, args.port, **sensor_kwargs) as bench:
        run_id = f"{started:%Y%m%d-%H%M%S}_{args.mode}_{bench.serial_number}"
        out = (ROOT / args.out).resolve() / run_id
        print(f"{BOLD}Campagne {run_id}{RESET}  (mode {args.mode.upper()}, firmware {bench.firmware_version})\n")
        for proc in ALL_PROCEDURES:
            try:
                r = proc(bench, limits)
            except Exception as exc:  # un test qui plante est un test en échec, la campagne continue
                name = proc.__name__
                r = TestResult(name[:3].upper(), name[4:], False, "exécution sans erreur",
                               {"erreur": f"{type(exc).__name__}: {exc}"})
            results.append(r)
            color = GREEN if r.passed else RED
            print(f"  {color}{r.verdict}{RESET}  {r.test_id}  {r.title}")
            for name, m in r.raw.items():
                m.save_csv(out / "raw" / f"{r.test_id}_{name}.csv")
        meta = dict(run_id=run_id, started_at=f"{started:%Y-%m-%d %H:%M:%S}", mode=args.mode,
                    serial_number=bench.serial_number, firmware=bench.firmware_version,
                    git_commit=git_commit())

    figures = {}
    if not args.no_plots:
        for r in results:
            path = plot_result(r, out / "figures")
            if path:
                figures[r.test_id] = path
    meta["duration_s"] = time.time() - t0

    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(
        {"meta": meta, "results": [dict(id=r.test_id, title=r.title, verdict=r.verdict, criterion=r.criterion,
                                        measures=r.measures) for r in results]},
        ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    write_summary_md(out / "summary.md", meta, results)
    report = write_html_report(out / "report.html", meta, results, figures)
    save_campaign(ROOT / args.out / "results.db", meta, results)

    if args.docs and figures:
        variant = "defectueux" if args.defective else args.mode
        for tid, src in figures.items():
            dest = tp_image_path(tid, variant)
            if dest is not None:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dest)
        print(f"Graphiques copiés dans les dossiers des TP (images/{variant}.png)")

    failed = [r for r in results if not r.passed]
    print()
    if failed:
        print(f"{RED}{BOLD}  ██  KO · CAPTEUR NON CONFORME  ({len(failed)} échec(s) : "
              f"{', '.join(r.test_id for r in failed)}){RESET}")
    else:
        print(f"{GREEN}{BOLD}  ██  OK · CAPTEUR CONFORME  ({len(results)}/{len(results)} tests){RESET}")
    shown = report.relative_to(ROOT) if report.is_relative_to(ROOT) else report
    print(f"\nRapport : {shown}  ·  durée {meta['duration_s']:.1f} s")
    return 1 if failed else 0


def write_summary_md(path: Path, meta: dict, results: list) -> None:
    lines = [f"# Campagne {meta['run_id']}", "",
             f"Mode {meta['mode'].upper()} · capteur {meta['serial_number']} · {meta['started_at']}", "",
             "| ID | Test | Verdict | Mesures clés | Critère |", "|---|---|---|---|---|"]
    for r in results:
        key = "; ".join(f"{k} = {v:.4g}" if isinstance(v, float) else f"{k} = {v}"
                        for k, v in list(r.measures.items())[:4])
        lines.append(f"| {r.test_id} | {r.title} | **{r.verdict}** | {key} | {r.criterion} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Banc de test automatisé pour capteur MPU6050")
    p.add_argument("--mode", choices=["sil", "hil"], default="sil", help="sil = simulation, hil = vrai matériel")
    p.add_argument("--port", help="port série de l'ESP32 en mode hil (COM3, /dev/ttyUSB0...)")
    p.add_argument("--serial", help="numéro de série du capteur testé")
    p.add_argument("--defective", action="store_true", help="(sil) simule un capteur hors tolérances")
    p.add_argument("--noise", type=float, help="(sil) bruit du capteur simulé en g (défaut 0.004)")
    p.add_argument("--offset-x", type=float, help="(sil) offset de l'axe X en g (défaut 0.035)")
    p.add_argument("--backlash", type=float, help="(sil) jeu mécanique du servo en degrés (défaut 0.4)")
    p.add_argument("--seed", type=int, help="(sil) graine du générateur de bruit")
    p.add_argument("--limits", default="config/limits.yaml")
    p.add_argument("--out", default="reports")
    p.add_argument("--no-plots", action="store_true")
    p.add_argument("--docs", action="store_true", help="copie chaque graphique dans le dossier de son TP (formation/05-tests-du-capteur)")
    sys.exit(run_campaign(p.parse_args()))


if __name__ == "__main__":
    main()
