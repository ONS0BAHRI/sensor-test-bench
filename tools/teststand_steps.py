"""Fonctions simples à appeler depuis NI TestStand (adaptateur Python) ou tout autre séquenceur.

Chaque fonction renvoie un nombre : dans TestStand, on l'appelle depuis une étape
« Numeric Limit Test » et c'est TestStand qui applique les limites et rédige le rapport.
Cela permet de comparer ton séquenceur Python (run_bench.py) avec un séquenceur industriel.

Utilisation dans TestStand :
    1. Adaptateur : Python, version 3.x installée sur le PC.
    2. Étape « Action » : ouvrir_banc("sil") ou ouvrir_banc("hil", "COM3").
    3. Étapes « Numeric Limit Test » : bruit_mg (limite haute 10), r2_linearite (limite basse 0.99)...
    4. Étape « Action » finale : fermer_banc().
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bench import open_bench  # noqa: E402
from bench import procedures as p  # noqa: E402

_bench = None
_limits = yaml.safe_load((ROOT / "config" / "limits.yaml").read_text(encoding="utf-8"))


def ouvrir_banc(mode: str = "sil", port: str = "") -> str:
    global _bench
    _bench = open_bench(mode, port or None)
    return f"{_bench.mode} {_bench.serial_number} firmware {_bench.firmware_version}"


def fermer_banc() -> None:
    global _bench
    if _bench is not None:
        _bench.close()
        _bench = None


def who_am_i() -> int:
    return _bench.identify()


def bruit_mg() -> float:
    r = p.t03_bruit(_bench, _limits)
    return max(v for k, v in r.measures.items() if k.startswith("écart-type"))


def r2_linearite() -> float:
    return p.t04_linearite(_bench, _limits).measures["R²"]


def hysteresis_mg() -> float:
    return p.t05_hysteresis(_bench, _limits).measures["écart max (mg)"]


def erreur_frequence_hz() -> float:
    return p.t07_frequence(_bench, _limits).measures["erreur max (Hz)"]


def temps_etablissement_ms() -> float:
    return p.t08_reponse(_bench, _limits).measures["temps d'établissement (ms)"]


if __name__ == "__main__":  # essai rapide sans TestStand
    print(ouvrir_banc("sil"))
    for fn in (who_am_i, bruit_mg, r2_linearite, hysteresis_mg, erreur_frequence_hz, temps_etablissement_ms):
        print(f"{fn.__name__:24s} {fn()}")
    fermer_banc()
