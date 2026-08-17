from .datos_generales import DatosGeneralesScreen
from .infraestructura import InfraestructuraScreen
from .acceso_remoto import AccesoRemotoScreen
from .estacion_camara import EstacionCamaraScreen
from .monitoreo_abiotico import MonitoreoAbioticoScreen
from .ubicaciones import UbicacionesScreen
from .activacion import ActivacionScreen
from .evidencias import EvidenciasScreen
from .configuracion_alarmas import ConfiguracionAlarmasScreen
from ..services.certificado_service import CertificadoService
from ..pdf.generador_pdf import GeneradorPDF
from .ui import (
    limpiar_pantalla, caja_doble, opcion_seccion, separador,
    breadcrumb, prompt, barra_acciones, progreso_global,
    notificacion_exito, notificacion_error, notificacion_info,
    encabezado_pegar, Color, Icono
)


class CertificadoMenu:

    def __init__(
        self,
        certificado: dict,
        centro: str,
        año: int
    ):
        from dataclasses import asdict
        if hasattr(certificado, "__dataclass_fields__"):
            self.certificado = asdict(certificado)
        else:
            self.certificado = certificado
        self.centro = centro
        self.año = año

    def _es_seccion_completada(self, num: int) -> bool:
        cert = self.certificado
        if num == 1:
            dg = cert.get("datos_generales", {})
            return any(bool(v) for k, v in dg.items() if k not in ("location", "nombre_centro"))
        elif num == 2:
            infra = cert.get("infraestructura", {})
            return any(bool(infra.get(k)) for k in ("categoria", "marca", "modelo", "serie", "sistema_operativo", "conectividad"))
        elif num == 3:
            ar = cert.get("acceso_remoto", {})
            return any(bool(v) for v in ar.values())
        elif num == 4:
            ec = cert.get("estacion_camara", {})
            return any(bool(v) for v in ec.values())
        elif num == 5:
            ma = cert.get("monitoreo_abiotico", {})
            return any(bool(v) for v in ma.values())
        elif num == 6:
            return bool(cert.get("ubicaciones"))
        elif num == 7:
            act = cert.get("activacion", {})
            return any(bool(v) for v in act.values())
        elif num == 8:
            dir_entrada = CertificadoService.obtener_carpeta_entrada()
            archivos = [
                f for f in dir_entrada.iterdir()
                if f.is_file() and not f.name.startswith(".")
            ] if dir_entrada.exists() else []
            return bool(archivos) or bool(cert.get("evidencias"))
        elif num == 9:
            ca = cert.get("configuracion_alarmas", [])
            if isinstance(ca, list):
                return len(ca) > 0
            elif isinstance(ca, dict):
                return any(bool(v) for v in ca.values())
        return False

    def _contar_seccion(self, num: int) -> tuple[int, int]:
        cert = self.certificado
        if num == 1:
            dg = cert.get("datos_generales", {})
            keys = ("encargado_area", "empresa", "location", "nombre_centro", "fecha_instalacion", "tecnico_visita", "numero_ficha")
            llenados = sum(1 for k in keys if bool(dg.get(k)))
            return llenados, len(keys)
        elif num == 2:
            infra = cert.get("infraestructura", {})
            keys = ("categoria", "marca", "modelo", "serie", "mac_ethernet", "ubicacion_pc", "sistema_operativo")
            llenados = sum(1 for k in keys if bool(infra.get(k)))
            return llenados, len(keys)
        elif num == 3:
            ar = cert.get("acceso_remoto", {})
            keys = ("protocolo", "tun0", "ip_fija", "puerto_server")
            llenados = sum(1 for k in keys if bool(ar.get(k)))
            return llenados, len(keys)
        elif num == 4:
            ec = cert.get("estacion_camara", {})
            keys = ("camara_instalada", "modelo_camara", "tipo_ip_camara", "conexion_camara", "estacion_instalada", "switch_poe")
            llenados = sum(1 for k in keys if bool(ec.get(k)))
            return llenados, len(keys)
        elif num == 5:
            ma = cert.get("monitoreo_abiotico", {})
            keys = ("instalado", "tipo_antena", "ubicacion_antena", "version", "mac", "panid")
            llenados = sum(1 for k in keys if bool(ma.get(k)))
            return llenados, len(keys)
        elif num == 6:
            ubis = len(cert.get("ubicaciones", []))
            reps = len(cert.get("equipos_repuesto", []))
            total_items = ubis + reps
            return total_items, max(1, total_items)
        elif num == 7:
            act = cert.get("activacion", {})
            keys = ("fecha_creacion_monitor", "tipo_ip", "ip_final", "ping_ok", "ssh_ok", "datos_visibles", "transmision_ok", "alarmas_activadas", "responsable_activacion", "estado_final")
            llenados = sum(1 for k in keys if bool(act.get(k)))
            return llenados, len(keys)
        elif num == 8:
            dir_entrada = CertificadoService.obtener_carpeta_entrada()
            archivos = [
                f for f in dir_entrada.iterdir()
                if f.is_file() and not f.name.startswith(".")
            ] if dir_entrada.exists() else []
            evs = len(archivos) or len(cert.get("evidencias", []))
            return evs, max(1, evs)
        elif num == 9:
            ca = cert.get("configuracion_alarmas", [])
            cnt = len(ca) if isinstance(ca, list) else (1 if ca else 0)
            return cnt, max(1, cnt)
        return 0, 1

    SECCIONES = [
        (1, "Datos Generales"),
        (2, "Infraestructura"),
        (3, "Acceso Remoto"),
        (4, "Est. Meteo./Cámara"),
        (5, "Monitoreo Abiótico"),
        (6, "Ubicaciones"),
        (7, "Activación"),
        (8, "Evidencias"),
        (9, "Config. Alarmas"),
    ]

    def mostrar(self):

        while True:

            limpiar_pantalla()

            # Calcular progreso global
            secciones_ok = sum(
                1 for num, _ in self.SECCIONES
                if self._es_seccion_completada(num)
            )
            total_secciones = len(self.SECCIONES)
            progreso_str = progreso_global(secciones_ok, total_secciones)

            # Header con caja
            nombre = self.certificado.get("datos_generales", {}).get("nombre_centro", self.centro)
            print()
            print(caja_doble(
                f"{Color.BOLD}Certificado: {nombre.upper()}{Color.RESET}",
                progreso_str
            ))
            print(breadcrumb("Inicio", nombre.upper()))
            print()

            # Secciones con progreso individual
            for num, titulo in self.SECCIONES:
                completados, total = self._contar_seccion(num)
                print(opcion_seccion(num, titulo, completados, total))

            print()
            print(separador())
            print()

            # Barra de acciones compacta
            print(barra_acciones(
                ("A", "Auto-rellenar"),
                ("G", "Guardar"),
                ("P", "Generar PDF"),
                ("E", "Eliminar"),
                ("V", "Volver"),
            ))

            opcion = input(prompt()).strip().upper()

            if opcion == "1":
                pantalla = DatosGeneralesScreen(
                    self.certificado
                )
                pantalla.mostrar()

            elif opcion == "2":
                InfraestructuraScreen(
                    self.certificado
                ).mostrar()

            elif opcion == "3":
                pantalla = (
                    AccesoRemotoScreen(
                        self.certificado
                    )
                )
                pantalla.mostrar()

            elif opcion == "4":
                EstacionCamaraScreen(
                    self.certificado
                ).mostrar()

            elif opcion == "5":
                MonitoreoAbioticoScreen(
                    self.certificado
                ).mostrar()

            elif opcion == "6":
                UbicacionesScreen(
                    self.certificado
                ).mostrar()

            elif opcion == "7":
                ActivacionScreen(
                    self.certificado
                ).mostrar()

            elif opcion == "8":
                EvidenciasScreen(
                    self.certificado
                ).mostrar()

            elif opcion == "9":
                ConfiguracionAlarmasScreen(
                    self.certificado
                ).mostrar()

            elif opcion == "A":
                self.autofill_comandos()

            elif opcion == "G":
                self.guardar()

            elif opcion == "P":
                self.generar_pdf()

            elif opcion == "E":
                if self.eliminar_certificado():
                    break

            elif opcion == "V":
                break

            else:
                print(notificacion_error("Opción inválida"))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def eliminar_certificado(self):
        try:
            location = self.certificado.get("datos_generales", {}).get("location", self.centro)
            confirmacion = input(f"\n  {Color.RED}¿Está seguro que desea ELIMINAR el certificado de '{location}'? [s/N]: {Color.RESET}").strip().lower()
            if confirmacion in ("s", "si"):
                exito = CertificadoService.eliminar_certificado(location, self.año)
                if exito:
                    print(notificacion_exito(f"Certificado de {location} eliminado exitosamente"))
                    input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
                    return True
                else:
                    print(notificacion_error("No se encontró el certificado para eliminar"))
        except Exception as e:
            print(notificacion_error(f"Error al eliminar certificado: {e}"))
        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
        return False

    def guardar(self):
        try:
            location = self.certificado.get("datos_generales", {}).get("location", self.centro)
            # Copiar evidencias desde la carpeta personal ~/evidencias_instalacion al histórico
            CertificadoService.copiar_evidencias_a_certificado(location, self.año)
            ruta_json = CertificadoService.guardar_certificado(
                certificado=self.certificado,
                location=location,
                año=self.año
            )
            print(notificacion_exito("Certificado guardado exitosamente"))
            print(f"  {Color.DIM}{ruta_json}{Color.RESET}")
        except Exception as e:
            print(notificacion_error(f"Error al guardar certificado: {e}"))
        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")

    def generar_pdf(self):
        try:
            location = self.certificado.get("datos_generales", {}).get("location", self.centro)
            # Copiar evidencias desde la carpeta personal ~/evidencias_instalacion al histórico
            CertificadoService.copiar_evidencias_a_certificado(location, self.año)
            dir_evidencias = CertificadoService.obtener_carpeta_evidencias(location, self.año)
            archivo_pdf = f"storage/certificados/{self.año}/{location}/certificado_inst_{location}.pdf"
            GeneradorPDF().generar(
                self.certificado,
                archivo_pdf,
                carpeta_evidencias=dir_evidencias
            )
            print(notificacion_exito("PDF generado exitosamente"))
            print(f"  {Color.DIM}{archivo_pdf}{Color.RESET}")
        except Exception as e:
            print(notificacion_error(f"Error al generar PDF: {e}"))
        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")

    def autofill_comandos(self):
        limpiar_pantalla()
        print()

        instrucciones = [
            "Copie y pegue la salida de cualquier comando:",
            "  'cmd status'   → Versión, MAC y Pan ID de antena",
            "  'cmd motes'    → Lista de motes",
            "  'ifconfig'     → Interfaz, MAC Ethernet, IP LAN y VPN",
            "  'hostnamectl'  → SO, Marca, Modelo y Categoría",
            "(Puede pegar múltiples comandos juntos)",
            "",
            "Ingrese 'FIN' o presione Enter dos veces al terminar",
        ]
        print(encabezado_pegar("AUTO-RELLENAR DESDE CONSOLA", instrucciones))
        print()

        lineas = []
        try:
            while True:
                linea = input()
                if linea.strip().upper() == "FIN":
                    break
                if not linea.strip() and lineas and not lineas[-1].strip():
                    break
                lineas.append(linea)
        except (EOFError, KeyboardInterrupt):
            pass

        texto = "\n".join(lineas)
        from certificado.utils.autofill import procesar_autofill
        res = procesar_autofill(self.certificado, texto)

        if not res["exito"]:
            print(notificacion_error("No se pudieron extraer datos de la salida pegada."))
            print(notificacion_info("Verifique haber copiado salidas de cmd status, ifconfig, hostnamectl o cmd motes."))
        else:
            print(notificacion_exito("DATOS EXTRAÍDOS Y APLICADOS AL CERTIFICADO:"))
            for cambio in res["resumen"]:
                print(f"    {Color.DIM}{Icono.ARROW} {cambio}{Color.RESET}")

        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")