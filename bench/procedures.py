"""Procédures de test T01 à T13 (le « quoi tester » du banc).

Chaque procédure :
1. pilote le banc (servo, vibreur, acquisition) à travers l'interface commune ;
2. calcule ses indicateurs avec le module processing ;
3. compare aux seuils de config/limits.yaml ;
4. renvoie un TestResult : verdict, mesures, critère, données brutes et données pour les graphiques.

Elles sont appelées à l'identique par pytest (tests/test_bench.py) et par la campagne
automatique (run_bench.py), en simulation comme sur le vrai matériel.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from processing import signal_tools as sp

from .base import Measurement, SensorError, SensorInterface
from .simulated_sensor import SimulatedSensor


@dataclass
class TestResult:
    test_id: str
    title: str
    passed: bool
    criterion: str
    measures: dict = field(default_factory=dict)       # valeurs mesurées affichées dans le rapport
    plot_data: dict = field(default_factory=dict)      # tableaux pour les graphiques
    raw: dict = field(default_factory=dict)            # nom -> Measurement (sauvé en CSV)
    notes: str = ""

    @property
    def verdict(self) -> str:
        return "OK" if self.passed else "KO"

    def summary(self) -> str:
        values = ", ".join(f"{k} = {_fmt(v)}" for k, v in self.measures.items())
        return f"[{self.verdict}] {self.test_id} {self.title} | {values} | critère : {self.criterion}"


def _fmt(v):
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def _static_mean(bench: SensorInterface, angle: float, lim: dict, axis: str = "ax") -> tuple[float, Measurement]:
    bench.set_angle(angle)
    bench.wait(lim["acquisition"]["settle_s"])
    m = bench.read(lim["acquisition"]["n_static"])
    return float(np.mean(getattr(m, axis))), m


# ---------------------------------------------------------------------------------------------
def t01_communication(bench: SensorInterface, lim: dict) -> TestResult:
    expected = lim["T01_communication"]["who_am_i"]
    value = bench.identify()
    return TestResult("T01", "Communication I2C", value == expected,
                      f"WHO_AM_I = 0x{expected:02X}", {"WHO_AM_I": f"0x{value:02X}"})


def t02_offset(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T02_offset"]
    bench.set_angle(0)
    bench.wait(lim["acquisition"]["settle_s"])
    expected = np.array([0.0, 0.0, 1.0])                         # capteur à plat : 1 g sur Z

    m1 = bench.read(c["n"])
    raw_offset = np.array([m1.ax.mean(), m1.ay.mean(), m1.az.mean()]) - expected

    m2 = bench.read(c["n"])                                      # nouvelle mesure, corrigée
    residual = np.array([m2.ax.mean(), m2.ay.mean(), m2.az.mean()]) - raw_offset - expected

    passed = bool(np.all(np.abs(raw_offset) <= c["max_raw_offset_g"])
                  and np.all(np.abs(residual) <= c["max_residual_g"]))
    measures = {f"offset brut {a} (g)": float(v) for a, v in zip("XYZ", raw_offset)}
    measures.update({f"résidu {a} après calibration (g)": float(v) for a, v in zip("XYZ", residual)})
    return TestResult("T02", "Offset et calibration", passed,
                      f"|offset brut| ≤ {c['max_raw_offset_g']} g et |résidu| ≤ {c['max_residual_g']} g",
                      measures, {"raw_offset": raw_offset, "residual": residual},
                      {"flat_1": m1, "flat_2": m2})


def t03_bruit(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T03_bruit"]
    bench.set_angle(0)
    bench.wait(lim["acquisition"]["settle_s"])
    m = bench.read(c["n"])
    stds = {a: float(np.std(getattr(m, a))) for a in ("ax", "ay", "az")}
    worst = max(stds.values())
    snr = sp.snr_db(1.0, worst)                                  # signal de référence : 1 g
    freqs, amp = sp.spectrum(m.az, bench.sample_rate)
    passed = worst <= c["max_std_g"] and snr >= c["min_snr_db"]
    measures = {f"écart-type {a} (mg)": v * 1000 for a, v in stds.items()}
    measures["SNR pour 1 g (dB)"] = snr
    return TestResult("T03", "Bruit au repos", passed,
                      f"écart-type ≤ {c['max_std_g'] * 1000:.0f} mg et SNR ≥ {c['min_snr_db']} dB",
                      measures, {"az": m.az, "ax": m.ax, "freqs": freqs, "amp": amp}, {"repos": m})


def t04_linearite(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T04_linearite"]
    angles = np.array(c["angles_deg"], float)
    bench.set_angle(-10)                                         # approche toujours par le même sens
    bench.wait(lim["acquisition"]["settle_s"])
    means, raws = [], {}
    for a in angles:
        mean, m = _static_mean(bench, a, lim)
        means.append(mean)
        raws[f"angle_{int(a):+03d}"] = m
    expected = np.sin(np.radians(angles))                        # en g
    fit = sp.linear_fit(expected, np.array(means))
    err_pct = fit.max_residual / c["full_scale_g"] * 100
    passed = fit.r2 >= c["min_r2"] and err_pct <= c["max_error_pct_fs"]
    return TestResult("T04", "Linéarité", passed,
                      f"R² ≥ {c['min_r2']} et erreur ≤ {c['max_error_pct_fs']} % PE",
                      {"R²": fit.r2, "erreur max (% PE)": err_pct, "gain mesuré": fit.gain,
                       "offset mesuré (g)": fit.offset},
                      {"angles": angles, "expected": expected, "measured": np.array(means),
                       "gain": fit.gain, "offset": fit.offset, "residuals": fit.residuals}, raws)


def t05_hysteresis(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T05_hysteresis"]
    angles = list(c["angles_deg"])
    bench.set_angle(angles[0] - 10)
    bench.wait(lim["acquisition"]["settle_s"])
    up = [_static_mean(bench, a, lim)[0] for a in angles]
    bench.set_angle(angles[-1] + 10)
    bench.wait(lim["acquisition"]["settle_s"])
    down = [_static_mean(bench, a, lim)[0] for a in reversed(angles)][::-1]
    gaps = np.abs(np.array(up) - np.array(down))
    worst = float(gaps.max())
    return TestResult("T05", "Hystérésis", worst <= c["max_gap_g"],
                      f"écart montée/descente ≤ {c['max_gap_g'] * 1000:.0f} mg",
                      {"écart max (mg)": worst * 1000, "à l'angle (°)": angles[int(gaps.argmax())]},
                      {"angles": np.array(angles), "up": np.array(up), "down": np.array(down)})


def t06_repetabilite(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T06_repetabilite"]
    values = []
    for _ in range(c["cycles"]):
        bench.set_angle(0)
        bench.wait(lim["acquisition"]["settle_s"])
        values.append(_static_mean(bench, c["angle_deg"], lim)[0])
    std = float(np.std(values, ddof=1))
    return TestResult("T06", "Répétabilité", std <= c["max_std_g"],
                      f"écart-type sur {c['cycles']} cycles ≤ {c['max_std_g'] * 1000:.0f} mg",
                      {"écart-type (mg)": std * 1000, "étendue (mg)": (max(values) - min(values)) * 1000},
                      {"values": np.array(values)})


def t07_frequence(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T07_frequence"]
    fs = bench.sample_rate
    bench.set_angle(0)
    bench.wait(lim["acquisition"]["settle_s"])
    found, spectra, raws = {}, {}, {}
    try:
        for f in c["frequencies_hz"]:
            bench.set_vibration(f)
            bench.wait(0.5)
            m = bench.read(c["n"])
            env = sp.envelope(m.az, fs, c["envelope_fc_hz"])
            found[f] = sp.dominant_frequency(env, fs, fmin=1.0, fmax=c["envelope_fc_hz"])
            spectra[f] = sp.spectrum(env, fs)
            raws[f"vibration_{f}Hz"] = m
            if f == c["frequencies_hz"][1]:
                raw_example = (m.t, m.az, env)
    finally:
        bench.set_vibration(0)
    errors = {f: abs(found[f] - f) for f in found}
    worst = max(errors.values())
    measures = {f"{f} Hz commandé -> mesuré (Hz)": found[f] for f in found}
    measures["erreur max (Hz)"] = worst
    return TestResult("T07", "Réponse en fréquence (FFT)", worst <= c["max_error_hz"],
                      f"pic FFT à ± {c['max_error_hz']} Hz de la fréquence commandée",
                      measures, {"spectra": spectra, "found": found, "example": raw_example}, raws)


def t08_reponse(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T08_reponse"]
    fs = bench.sample_rate
    bench.set_angle(0)
    bench.wait(0.6)
    m = bench.step(c["angle_deg"], c["n"])
    t = m.t
    t_step = t[c["n"] // 10]
    filtered = sp.butter_lowpass(m.ax, fs, c["filter_fc_hz"])
    r = sp.step_response(t, filtered, t_step, c["tolerance"])
    return TestResult("T08", "Temps de réponse", r.settling_time_s <= c["max_settling_s"],
                      f"temps d'établissement à {c['tolerance'] * 100:.0f} % ≤ {c['max_settling_s'] * 1000:.0f} ms",
                      {"temps de montée 10-90 % (ms)": r.rise_time_s * 1000,
                       "temps d'établissement (ms)": r.settling_time_s * 1000,
                       "dépassement (%)": r.overshoot_pct},
                      {"t": t, "raw": m.ax, "filtered": filtered, "t_step": t_step,
                       "initial": r.initial, "final": r.final, "settle": r.settling_time_s,
                       "tol": c["tolerance"]}, {"echelon": m})


def t09_filtre(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T09_filtre"]
    fs = bench.sample_rate
    _, m = _static_mean(bench, c["angle_deg"], {**lim, "acquisition": {**lim["acquisition"], "n_static": c["n"]}})
    raw = m.ax
    filtered = sp.butter_lowpass(raw, fs, c["fc_hz"])
    reduction = (1 - np.std(filtered) / np.std(raw)) * 100
    shift = abs(filtered.mean() - raw.mean()) / abs(raw.mean()) * 100
    passed = reduction >= c["min_noise_reduction_pct"] and shift <= c["max_mean_shift_pct"]
    return TestResult("T09", "Validation du filtre passe-bas", passed,
                      f"bruit réduit ≥ {c['min_noise_reduction_pct']} % et niveau décalé ≤ {c['max_mean_shift_pct']} %",
                      {"bruit brut (mg)": float(np.std(raw)) * 1000,
                       "bruit filtré (mg)": float(np.std(filtered)) * 1000,
                       "réduction du bruit (%)": float(reduction), "décalage du niveau (%)": float(shift)},
                      {"t": m.t, "raw": raw, "filtered": filtered, "fc": c["fc_hz"]}, {"statique_30deg": m})


def t10_echantillonnage(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T10_echantillonnage"]
    m = bench.read(c["n"])
    rate, jitter = sp.effective_sample_rate(m.t_us)
    err = abs(rate - bench.sample_rate) / bench.sample_rate * 100
    passed = err <= c["max_rate_error_pct"] and jitter <= c["max_jitter_pct"]
    return TestResult("T10", "Fréquence d'échantillonnage réelle", passed,
                      f"écart ≤ {c['max_rate_error_pct']} % et gigue ≤ {c['max_jitter_pct']} %",
                      {"fréquence nominale (Hz)": bench.sample_rate, "fréquence mesurée (Hz)": rate,
                       "écart (%)": err, "gigue (%)": jitter},
                      {"dt_us": np.diff(m.t_us)})


def t12_robustesse(bench: SensorInterface, lim: dict) -> TestResult:
    checks = {}

    def expect(name, exc_type, fn):
        try:
            fn()
            checks[name] = "KO : aucune erreur levée"
        except exc_type as exc:
            checks[name] = f"OK : {type(exc).__name__}"
        except Exception as exc:  # erreur non prévue = plantage mal géré
            checks[name] = f"KO : {type(exc).__name__} inattendue ({exc})"

    expect("angle hors plage (200°)", ValueError, lambda: bench.set_angle(200))
    expect("acquisition de 0 point", ValueError, lambda: bench.read(0))
    expect("commande série inconnue", SensorError, lambda: bench.raw_command("FOO"))
    if bench.mode == "sil":
        expect("capteur débranché", SensorError, lambda: SimulatedSensor(disconnected=True).identify())
    still_ok = bench.identify() == lim["T01_communication"]["who_am_i"]
    checks["banc toujours opérationnel après les erreurs"] = "OK" if still_ok else "KO"
    passed = all(v.startswith("OK") for v in checks.values())
    return TestResult("T12", "Robustesse aux erreurs", passed,
                      "chaque erreur est signalée proprement, sans plantage", checks,
                      notes="En HIL, le débranchement du câble se teste à la main (voir README).")


def t13_defauts(bench: SensorInterface, lim: dict) -> TestResult:
    c = lim["T13_defauts"]
    fs = bench.sample_rate
    bench.set_angle(0)
    bench.wait(lim["acquisition"]["settle_s"])
    m = bench.read(c["n"])
    params = dict(spike_z=c["spike_z"], stuck_run=c["stuck_run"],
                  drift_max=c["drift_max_g_per_s"], noise_max=c["noise_max_g"])
    healthy = sp.detect_faults(m.ax, fs, **params)
    false_alarms = [f for f in sp.FAULTS if healthy[f]]
    detected, signals = {}, {"sain": m.ax}
    for fault in sp.FAULTS:
        y = sp.inject_fault(m.ax, fault, fs)
        signals[fault] = y
        detected[fault] = sp.detect_faults(y, fs, **params)[fault]
    rate = sum(detected.values()) / len(detected) * 100
    passed = rate == 100 and not false_alarms
    measures = {f"défaut {f}": "détecté" if d else "MANQUÉ" for f, d in detected.items()}
    measures["taux de détection (%)"] = rate
    measures["fausses alarmes sur signal sain"] = ", ".join(false_alarms) or "aucune"
    return TestResult("T13", "Détection de défauts injectés", passed,
                      "100 % des défauts détectés, 0 fausse alarme", measures,
                      {"signals": signals, "t": m.t, "indicators": healthy["_indicateurs"]}, {"repos": m})


ALL_PROCEDURES = [t01_communication, t02_offset, t03_bruit, t04_linearite, t05_hysteresis,
                  t06_repetabilite, t07_frequence, t08_reponse, t09_filtre, t10_echantillonnage,
                  t12_robustesse, t13_defauts]
