"""Tests du pilote série RealSensor contre un faux ESP32 (aucun matériel nécessaire)."""
import numpy as np
import pytest
import yaml

import bench.real_sensor as real_sensor
from bench import SensorError
from bench.procedures import ALL_PROCEDURES

from .conftest import ROOT
from .fake_firmware import FakeSerial


def open_fake(monkeypatch, **fake_kwargs):
    holder = {}

    def factory(port, baudrate, timeout):
        holder["dev"] = FakeSerial(port, baudrate, timeout, **fake_kwargs)
        return holder["dev"]

    monkeypatch.setattr(real_sensor.serial, "Serial", factory)
    # le temps qui passe côté PC fait avancer la physique simulée côté « ESP32 »
    monkeypatch.setattr(real_sensor.time, "sleep", lambda s: holder["dev"].sim.wait(s) if "dev" in holder else None)
    return real_sensor.RealSensor("FAKE"), holder


def test_handshake_reads_version_and_rate(monkeypatch):
    sensor, _ = open_fake(monkeypatch)
    assert sensor.firmware_version == "1.0.0"
    assert sensor.sample_rate == 500
    assert sensor.identify() == 0x68


def test_raw_values_are_converted_to_physical_units(monkeypatch):
    sensor, _ = open_fake(monkeypatch)
    m = sensor.read(500)
    assert len(m) == 500
    assert np.mean(m.az) == pytest.approx(1.0, abs=0.1)          # 1 g à plat
    assert 20 < np.mean(m.temp) < 35                              # °C
    assert np.all(np.diff(m.t_us) > 0)


def test_firmware_error_becomes_sensor_error(monkeypatch):
    sensor, _ = open_fake(monkeypatch)
    with pytest.raises(SensorError, match="commande inconnue"):
        sensor.raw_command("FOO")


def test_disconnected_sensor_is_reported(monkeypatch):
    sensor, _ = open_fake(monkeypatch, disconnected=True)
    with pytest.raises(SensorError, match="absent"):
        sensor.identify()
    with pytest.raises(SensorError):
        sensor.read(10)


def test_close_stops_vibration_and_port(monkeypatch):
    sensor, holder = open_fake(monkeypatch)
    sensor.set_vibration(10)
    sensor.close()
    assert holder["dev"].closed
    assert holder["dev"].sim._vib == 0


@pytest.mark.parametrize("procedure", ALL_PROCEDURES, ids=lambda p: p.__name__)
def test_full_campaign_through_serial_driver(monkeypatch, procedure):
    limits = yaml.safe_load((ROOT / "config" / "limits.yaml").read_text(encoding="utf-8"))
    sensor, _ = open_fake(monkeypatch)
    result = procedure(sensor, limits)
    assert result.passed, result.summary()
