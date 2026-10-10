"""Lien entre le code et la formation : où ranger les graphiques de chaque test."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "formation" / "05-tests-du-capteur"

TP_FOLDERS = {
    "T01": "TP01-communication-i2c",
    "T02": "TP02-offset-et-calibration",
    "T03": "TP03-bruit",
    "T04": "TP04-linearite",
    "T05": "TP05-hysteresis",
    "T06": "TP06-repetabilite",
    "T07": "TP07-reponse-en-frequence",
    "T08": "TP08-temps-de-reponse",
    "T09": "TP09-filtre-numerique",
    "T10": "TP10-echantillonnage",
    "T11": "TP11-derive-thermique",
    "T12": "TP12-robustesse",
    "T13": "TP13-detection-de-defauts",
}


def tp_image_path(test_id: str, variant: str) -> Path | None:
    """Chemin de l'image d'un TP : variant = 'sil', 'hil' ou 'defectueux'."""
    folder = TP_FOLDERS.get(test_id)
    if folder is None:
        return None
    return TESTS_DIR / folder / "images" / f"{variant}.png"
