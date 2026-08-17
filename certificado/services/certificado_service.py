from pathlib import Path
from datetime import datetime
from dataclasses import asdict
import json
import uuid
# pyrefly: ignore [missing-import]
from certificado.models.certificado import Certificado
from certificado.models.metadata import Metadata

BASE_STORAGE = Path("storage/certificados")

class CertificadoService:

    @staticmethod
    def crear_certificado(
        location: str,
        nombre_centro: str
    ) -> Certificado:

        ahora = datetime.now()

        metadata = Metadata(
            uuid=str(uuid.uuid4()),
            version_modelo="1.0",
            fecha_creacion=ahora.isoformat(),
            fecha_modificacion=ahora.isoformat()
        )

        certificado = Certificado(

            metadata=metadata,

            datos_generales={
                "encargado_area": "",
                "empresa": "",
                "location": location,
                "nombre_centro": nombre_centro,
                "fecha_instalacion": "",
                "tecnico_visita": "",
                "numero_ficha": ""
            },

            infraestructura={
                "categoria": "",
                "marca": "",
                "modelo": "",
                "sistema_operativo": "",
                "conectividad": "",
                "switch": "",
                "puerto": ""
            },

            acceso_remoto={
                "protocolo": "",
                "tun0": "",
                "ip_fija": "",
                "puerto_server": ""
            },

            estacion_camara={
                "camara_instalada": "",
                "modelo_camara": "",
                "ip_fija_camara": "",
                "conexion_camara": "",

                "estacion_instalada": "",
                "modelo_estacion": "",
                "region_davis": ""
            },

            monitoreo_abiotico={
                "instalado": "",
                "version": "",
                "mac": "",
                "panid": ""
            },

            activacion={
                "fecha_creacion_monitor": ahora.strftime("%d/%m/%Y"),
                "tipo_ip": "",
                "ip_fija": "",
                "ip_final": "",
                "ping_ok": False,
                "ssh_ok": False,
                "datos_visibles": False,
                "transmision_ok": False,
                "alarmas_activadas": False,
                "responsable_activacion": "",
                "estado_final": ""
            },

            ubicaciones=[],
            equipos_repuesto=[],
            configuracion_alarmas=[]
        )

        return certificado
    

    @staticmethod
    def guardar_certificado(
        certificado: Certificado | dict,
        location: str,
        año: int
    ) -> Path:

        ruta_certificado = (
            BASE_STORAGE /
            str(año) /
            location
        )

        ruta_certificado.mkdir(
            parents=True,
            exist_ok=True
        )
        # Asegurar la creación estática de la carpeta evidencias
        (ruta_certificado / "evidencias").mkdir(parents=True, exist_ok=True)


        archivo_json = (
            ruta_certificado /
            "certificado.json"
        )

        with open(
            archivo_json,
            "w",
            encoding="utf-8"
        ) as archivo:

            if isinstance(certificado, Certificado):
                contenido = asdict(certificado)
            elif isinstance(certificado, dict):
                contenido = certificado
            elif hasattr(certificado, "__dataclass_fields__"):
                # pyrefly: ignore [bad-argument-type]
                contenido = asdict(certificado)
            else:
                contenido = certificado

            json.dump(
                contenido,
                archivo,
                indent=4,
                ensure_ascii=False
            )

        return archivo_json

    @staticmethod
    def obtener_carpeta_entrada() -> Path:
        """Obtiene y asegura la existencia de la carpeta personal ~/evidencias_instalacion."""
        entrada = Path.home() / "evidencias_instalacion"
        entrada.mkdir(parents=True, exist_ok=True)
        return entrada

    @staticmethod
    def limpiar_carpeta_entrada() -> int:
        """Limpia todos los archivos dentro de ~/evidencias_instalacion para un nuevo certificado."""
        dir_entrada = CertificadoService.obtener_carpeta_entrada()
        eliminados = 0
        for f in dir_entrada.iterdir():
            if f.is_file() and not f.name.startswith("."):
                f.unlink()
                eliminados += 1
        return eliminados

    @staticmethod
    def copiar_evidencias_a_certificado(location: str, año: int) -> int:
        """Copia las evidencias desde ~/evidencias_instalacion al historico storage/certificados/<AÑO>/<LOCATION>/evidencias/."""
        dir_entrada = CertificadoService.obtener_carpeta_entrada()
        dir_destino = CertificadoService.obtener_carpeta_evidencias(location, año)
        copiados = 0
        for f in dir_entrada.iterdir():
            if f.is_file() and not f.name.startswith("."):
                dest = dir_destino / f.name
                dest.write_bytes(f.read_bytes())
                copiados += 1
        return copiados

    @staticmethod
    def obtener_carpeta_evidencias(
        location: str,
        año: int
    ) -> Path:
        ruta_evidencias = BASE_STORAGE / str(año) / location / "evidencias"
        ruta_evidencias.mkdir(parents=True, exist_ok=True)
        return ruta_evidencias

    @staticmethod
    def listar_certificados(
        año: int
    ) -> list[str]:

        ruta = BASE_STORAGE / str(año)

        if not ruta.exists():
            return []

        certificados = []

        for carpeta in ruta.iterdir():

            if not carpeta.is_dir():
                continue

            archivo_json = carpeta / "certificado.json"

            if archivo_json.exists():
                certificados.append(carpeta.name)

        return sorted(certificados)

    @staticmethod
    def cargar_certificado(
        location: str,
        año: int
    )-> dict:

        archivo_json = (
            BASE_STORAGE /
            str(año) /
            location /
            "certificado.json"
        )

        if not archivo_json.exists():
            raise FileNotFoundError(
                f"No existe certificado para {location}"
            )

        with open(
            archivo_json,
            "r",
            encoding="utf-8"
        ) as archivo:

            return json.load(archivo)

    @staticmethod
    def eliminar_certificado(
        location: str,
        año: int
    ) -> bool:
        """Elimina la carpeta completa del certificado (JSON, PDF y evidencias)."""
        import shutil
        dir_cert = BASE_STORAGE / str(año) / location
        if dir_cert.exists() and dir_cert.is_dir():
            shutil.rmtree(dir_cert)
            return True
        return False

