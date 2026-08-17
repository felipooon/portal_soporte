from certificado.services.certificado_service import CertificadoService
from .ui import (
    limpiar_pantalla, caja, separador, breadcrumb,
    opcion_menu, prompt, item_archivo, texto_vacio, campo,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    Color, Icono
)


class EvidenciasScreen:

    def __init__(self, certificado: dict):
        self.certificado = certificado
        if "evidencias" not in self.certificado:
            self.certificado["evidencias"] = []

    def mostrar(self):
        while True:
            dir_entrada = CertificadoService.obtener_carpeta_entrada()
            archivos_entrada = [
                f.name for f in dir_entrada.iterdir()
                if f.is_file() and not f.name.startswith(".")
            ] if dir_entrada.exists() else []

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}EVIDENCIAS FOTOGRÁFICAS Y DOCUMENTOS{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Evidencias"))
            print()

            print(campo("Carpeta de entrada", str(dir_entrada)))
            print()

            if archivos_entrada:
                print(f"  {Color.BOLD}Archivos detectados:{Color.RESET}")
                for idx, nombre in enumerate(archivos_entrada, start=1):
                    print(item_archivo(nombre, "+"))
            else:
                print(texto_vacio("No existen archivos en ~/evidencias_instalacion."))
                print(f"  {Color.DIM}Por favor arrastre aquí las fotos y la planilla de alarmas.{Color.RESET}")

            print()
            print(separador())
            print()
            print(opcion_menu("L", "Limpiar carpeta de evidencias (para nuevo centro)"))
            print(opcion_menu("V", "Volver"))
            print()

            opcion = input(prompt()).strip().upper()

            if opcion == "L":
                self.limpiar_evidencias()
            elif opcion == "V":
                break
            else:
                print(notificacion_error("Opción inválida"))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def limpiar_evidencias(self):
        print()
        confirm = input(
            f"  {Color.YELLOW}{Icono.BULLET} ¿Desea borrar todos los archivos en ~/evidencias_instalacion? [s/N]: {Color.RESET}"
        ).strip().lower()
        if confirm == 's':
            borrados = CertificadoService.limpiar_carpeta_entrada()
            print(notificacion_exito(f"Se eliminaron {borrados} archivos de ~/evidencias_instalacion."))
        else:
            print(notificacion_advertencia("Operación cancelada."))
        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
