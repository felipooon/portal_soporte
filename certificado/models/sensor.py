from dataclasses import dataclass


@dataclass
class Sensor:
    tipo: str = ""
    profundidad: str = ""
    serial: str = ""