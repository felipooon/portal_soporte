from dataclasses import dataclass
from certificado.models.sensor import Sensor

@dataclass
class Equipo:
    numero_equipo: int = 0
    mac: str = ""
    sensor: Sensor | None = None