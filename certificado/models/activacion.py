from dataclasses import dataclass


@dataclass
class Activacion:
    fecha_creacion_monitor: str = ""

    tipo_ip: str = ""
    ip_final: str = ""

    ping_ok: bool = False
    ssh_ok: bool = False
    datos_visibles: bool = False
    transmision_ok: bool = False
    alarmas_activadas: bool = False

    responsable_activacion: str = ""

    estado_final: str = ""