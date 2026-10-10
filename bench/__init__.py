from .base import Measurement, SensorError, SensorInterface
from .simulated_sensor import SimulatedSensor


def open_bench(mode: str = "sil", port: str | None = None, **kwargs) -> SensorInterface:
    """Ouvre le banc en simulation ('sil') ou sur le vrai matériel ('hil')."""
    if mode == "sil":
        return SimulatedSensor(**kwargs)
    if mode == "hil":
        if not port:
            raise ValueError("Le mode HIL demande un port série, par exemple --port COM3 ou /dev/ttyUSB0")
        from .real_sensor import RealSensor
        return RealSensor(port, **kwargs)
    raise ValueError(f"Mode inconnu : {mode} (attendu : sil ou hil)")


__all__ = ["Measurement", "SensorError", "SensorInterface", "SimulatedSensor", "open_bench"]
