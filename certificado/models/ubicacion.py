from dataclasses import dataclass, field

@dataclass
class Ubicacion:

    nombre: str = ""

    elementos: list[str] = field(
        default_factory=list
    )