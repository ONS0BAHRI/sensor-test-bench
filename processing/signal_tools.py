"""Boîte à outils de traitement du signal utilisée par les procédures de test.

Chaque fonction est petite, documentée et couverte par des tests unitaires
(tests/test_signal_tools.py).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import signal as sps


# --- Filtrage ------------------------------------------------------------------------------
def moving_average(x: np.ndarray, width: int) -> np.ndarray:
    """Moyenne glissante centrée (mode 'same')."""
    if width < 1:
        raise ValueError("width doit être >= 1")
    return np.convolve(x, np.ones(width) / width, mode="same")


def butter_lowpass(x: np.ndarray, fs: float, fc: float, order: int = 4) -> np.ndarray:
    """Filtre passe-bas Butterworth à phase nulle (aller-retour, pas de retard)."""
    if not 0 < fc < fs / 2:
        raise ValueError(f"La fréquence de coupure {fc} Hz doit être entre 0 et fs/2 = {fs / 2} Hz")
    sos = sps.butter(order, fc, btype="low", fs=fs, output="sos")
    return sps.sosfiltfilt(sos, x)


def envelope(x: np.ndarray, fs: float, fc: float = 60.0) -> np.ndarray:
    """Enveloppe d'une vibration : redressement puis passe-bas.

    Le vibreur tourne vite (~170 Hz) ; on ne cherche pas cette porteuse mais la fréquence
    à laquelle le banc l'allume et l'éteint. Elle apparaît dans l'enveloppe.
    """
    return butter_lowpass(np.abs(x - np.mean(x)), fs, fc)


# --- Analyse fréquentielle -------------------------------------------------------------------
def spectrum(x: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Spectre d'amplitude unilatéral avec fenêtre de Hann (composante continue retirée)."""
    x = np.asarray(x, float) - np.mean(x)
    w = np.hanning(len(x))
    amp = np.abs(np.fft.rfft(x * w)) * 2 / np.sum(w)
    freqs = np.fft.rfftfreq(len(x), 1 / fs)
    return freqs, amp


def dominant_frequency(x: np.ndarray, fs: float, fmin: float = 0.5, fmax: float | None = None) -> float:
    """Fréquence du pic principal dans [fmin, fmax], affinée par interpolation parabolique."""
    freqs, amp = spectrum(x, fs)
    fmax = fmax or fs / 2
    band = np.where((freqs >= fmin) & (freqs <= fmax))[0]
    k = band[np.argmax(amp[band])]
    if 0 < k < len(amp) - 1:
        a, b, c = amp[k - 1], amp[k], amp[k + 1]
        denom = a - 2 * b + c
        shift = 0.5 * (a - c) / denom if denom != 0 else 0.0
        return float(freqs[k] + shift * (freqs[1] - freqs[0]))
    return float(freqs[k])


# --- Indicateurs statiques -------------------------------------------------------------------
def snr_db(signal_level: float, noise_std: float) -> float:
    """Rapport signal sur bruit en dB : 20·log10(niveau / écart-type du bruit)."""
    return float(20 * np.log10(abs(signal_level) / noise_std))


@dataclass
class LinearFit:
    gain: float
    offset: float
    r2: float
    max_residual: float       # même unité que la mesure
    residuals: np.ndarray


def linear_fit(expected: np.ndarray, measured: np.ndarray) -> LinearFit:
    """Régression measured = gain·expected + offset (moindres carrés)."""
    expected = np.asarray(expected, float)
    measured = np.asarray(measured, float)
    gain, offset = np.polyfit(expected, measured, 1)
    fitted = gain * expected + offset
    residuals = measured - fitted
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((measured - measured.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return LinearFit(float(gain), float(offset), float(r2), float(np.max(np.abs(residuals))), residuals)


# --- Indicateurs dynamiques ------------------------------------------------------------------
@dataclass
class StepResponse:
    initial: float
    final: float
    rise_time_s: float        # 10 % -> 90 %
    settling_time_s: float    # entrée définitive dans la bande ±tol
    overshoot_pct: float


def step_response(t: np.ndarray, x: np.ndarray, t_step: float, tol: float = 0.05) -> StepResponse:
    """Caractérise une réponse indicielle déjà filtrée."""
    before = x[t < t_step]
    initial = float(np.mean(before[-max(len(before) // 2, 1):]))
    final = float(np.mean(x[int(len(x) * 0.8):]))
    amp = final - initial
    if abs(amp) < 1e-9:
        raise ValueError("Pas de saut détectable dans le signal")
    norm = (x - initial) / amp
    after = t >= t_step
    ta, na = t[after], norm[after]

    def first_cross(level):
        idx = np.where(na >= level)[0]
        return float(ta[idx[0]]) if len(idx) else float("nan")

    rise = first_cross(0.9) - first_cross(0.1)
    outside = np.where(np.abs(na - 1.0) > tol)[0]
    settle_t = float(ta[outside[-1] + 1]) if len(outside) and outside[-1] + 1 < len(ta) else float(ta[0])
    overshoot = max(0.0, float(np.max(na) - 1.0) * 100)
    return StepResponse(initial, final, rise, settle_t - t_step, overshoot)


def effective_sample_rate(t_us: np.ndarray) -> tuple[float, float]:
    """Fréquence d'échantillonnage réelle (Hz) et gigue (écart-type de la période, en %)."""
    dt = np.diff(np.asarray(t_us, float)) / 1e6
    return float(1 / np.mean(dt)), float(np.std(dt) / np.mean(dt) * 100)


# --- Détection de défauts --------------------------------------------------------------------
FAULTS = ("pic", "saturation", "fige", "derive", "bruit_fort")


def detect_faults(x: np.ndarray, fs: float, full_scale: float = 2.0, spike_z: float = 8.0,
                  stuck_run: int = 50, drift_max: float = 0.01, noise_max: float = 0.02) -> dict:
    """Détection de défauts par règles simples et explicables.

    - pic        : un échantillon s'écarte de plus de spike_z écarts robustes (MAD) de la médiane
    - saturation : au moins 3 échantillons à 98 % de la pleine échelle
    - figé       : au moins stuck_run valeurs identiques consécutives (un vrai capteur bruite)
    - dérive     : pente de la régression linéaire > drift_max (g/s)
    - bruit fort : bruit estimé par les différences successives > noise_max (g)
    """
    x = np.asarray(x, float)
    med = np.median(x)
    mad = 1.4826 * np.median(np.abs(x - med)) or 1e-12
    robust_z = np.max(np.abs(x - med)) / mad

    sat_count = int(np.sum(np.abs(x) >= 0.98 * full_scale))

    same = np.concatenate([[False], np.diff(x) == 0])
    longest, run = 0, 0
    for s in same:
        run = run + 1 if s else 0
        longest = max(longest, run + 1 if s else 1)

    t = np.arange(len(x)) / fs
    slope = float(np.polyfit(t, x, 1)[0])
    noise = float(np.std(np.diff(x)) / np.sqrt(2))

    return {
        "pic": bool(robust_z > spike_z),
        "saturation": sat_count >= 3,
        "fige": longest >= stuck_run,
        "derive": abs(slope) > drift_max,
        "bruit_fort": noise > noise_max,
        "_indicateurs": {"robust_z": float(robust_z), "n_satures": sat_count, "plus_longue_serie": longest,
                         "pente_g_par_s": slope, "bruit_g": noise},
    }


def inject_fault(x: np.ndarray, fault: str, fs: float, seed: int = 0) -> np.ndarray:
    """Injecte un défaut connu dans un signal sain (sert à valider le détecteur)."""
    rng = np.random.default_rng(seed)
    y = np.array(x, float, copy=True)
    n = len(y)
    if fault == "pic":
        y[n // 3] += 0.5
    elif fault == "saturation":
        y[n // 2: n // 2 + 20] = 32767 / 16384
    elif fault == "fige":
        y[n // 2:] = y[n // 2]
    elif fault == "derive":
        y += 0.05 * np.arange(n) / fs
    elif fault == "bruit_fort":
        y += rng.normal(0, 0.05, n)
    else:
        raise ValueError(f"Défaut inconnu : {fault}")
    return y
