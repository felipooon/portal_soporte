from dataclasses import dataclass, field

from certificado.models.activacion import Activacion
from certificado.models.evidencia import Evidencia
from certificado.models.metadata import Metadata
from certificado.models.ubicacion import Ubicacion


@dataclass
class Certificado:

    metadata: Metadata = field(
        default_factory=Metadata
    )

    datos_generales: dict = field(
        default_factory=dict
    )

    infraestructura: dict = field(
        default_factory=dict
    )

    acceso_remoto: dict = field(
        default_factory=dict
    )

    estacion_camara: dict = field(
        default_factory=dict
    )

    monitoreo_abiotico: dict = field(
        default_factory=dict
    )

    ubicaciones: list = field(
        default_factory=list
    )

    activacion: Activacion = field(
        default_factory=Activacion
    )

    observaciones: str = ""

    evidencias: list[Evidencia] = field(
        default_factory=list
    )

    equipos_repuesto: list = field(
        default_factory=list
    )

    configuracion_alarmas: list = field(
        default_factory=list
    )