"""Tests unitaires du traitement du signal, sur des signaux dont on connaît la réponse exacte."""
import numpy as np
import pytest

from processing import signal_tools as sp

FS = 500.0


def sine(freq, n=2000, amp=1.0):
    t = np.arange(n) / FS
    return t, amp * np.sin(2 * np.pi * freq * t)


def test_dominant_frequency_finds_sine():
    _, x = sine(12.3)
    assert sp.dominant_frequency(x, FS) == pytest.approx(12.3, abs=0.05)


def test_spectrum_amplitude_of_a_sine():
    _, x = sine(25.0, amp=0.2)
    freqs, amp = sp.spectrum(x, FS)
    assert amp[np.argmin(abs(freqs - 25.0))] == pytest.approx(0.2, rel=0.05)


def test_lowpass_keeps_slow_signal_and_removes_fast_one():
    _, slow = sine(2.0)
    _, fast = sine(150.0)
    out = sp.butter_lowpass(slow + fast, FS, fc=20)
    core = slice(200, -200)   # on ignore les bords
    assert np.max(np.abs(out[core] - slow[core])) < 0.01


def test_lowpass_rejects_invalid_cutoff():
    with pytest.raises(ValueError):
        sp.butter_lowpass(np.zeros(100), FS, fc=300)


def test_envelope_reveals_modulation_frequency():
    t = np.arange(4000) / FS
    gate = ((t * 8.0) % 1.0 < 0.5).astype(float)
    x = gate * 0.1 * np.sin(2 * np.pi * 170 * t)
    env = sp.envelope(x, FS)
    assert sp.dominant_frequency(env, FS, fmin=1, fmax=60) == pytest.approx(8.0, abs=0.2)


def test_linear_fit_recovers_gain_and_offset():
    x = np.linspace(0, 1, 10)
    fit = sp.linear_fit(x, 1.03 * x + 0.02)
    assert fit.gain == pytest.approx(1.03)
    assert fit.offset == pytest.approx(0.02)
    assert fit.r2 == pytest.approx(1.0)


def test_snr_db():
    assert sp.snr_db(1.0, 0.01) == pytest.approx(40.0)


def test_step_response_of_first_order_system():
    t = np.arange(1000) / FS
    tau = 0.05
    x = np.where(t < 0.2, 0.0, 1 - np.exp(-(t - 0.2) / tau))
    r = sp.step_response(t, x, t_step=0.2, tol=0.05)
    assert r.settling_time_s == pytest.approx(3 * tau, abs=0.01)      # 5 % ≈ 3 τ
    assert r.rise_time_s == pytest.approx(2.2 * tau, abs=0.01)        # 10-90 % ≈ 2,2 τ


def test_effective_sample_rate():
    rate, jitter = sp.effective_sample_rate(np.arange(0, 2_000_000, 2000))
    assert rate == pytest.approx(500.0)
    assert jitter == pytest.approx(0.0)


@pytest.fixture
def healthy_signal():
    rng = np.random.default_rng(1)
    return 0.03 + np.round(rng.normal(0, 0.004, 2000) * 16384) / 16384


def test_no_false_alarm_on_healthy_signal(healthy_signal):
    flags = sp.detect_faults(healthy_signal, FS)
    assert not any(flags[f] for f in sp.FAULTS)


@pytest.mark.parametrize("fault", sp.FAULTS)
def test_each_injected_fault_is_detected(healthy_signal, fault):
    y = sp.inject_fault(healthy_signal, fault, FS)
    assert sp.detect_faults(y, FS)[fault]
