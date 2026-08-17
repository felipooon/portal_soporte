from dataclasses import dataclass


@dataclass
class Metadata:
    uuid: str = ""

    version_modelo: str = "1.0"

    fecha_creacion: str = ""
    fecha_modificacion: str = ""