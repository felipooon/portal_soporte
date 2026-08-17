import copy
from datetime import datetime
from ..utils.input_helpers import (
    pedir_con_default,
    pedir_fecha_con_default,
    pedir_opcion_si_no,
    pedir_tipo_ip,
    pedir_ip,
    CancelarEdicionException,
    GuardarAvanceException
)
from .ui import (
    limpiar_pantalla, caja, campo, campo_bool, separador, breadcrumb,
    opcion_menu, prompt, encabezado_edicion,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    Color, Icono
)


class ActivacionScreen:

    def __init__(self, certificado: dict):
        self.certificado = certificado
        hoy = datetime.now().strftime("%d/%m/%Y")
        if "activacion" not in self.certificado:
            self.certificado["activacion"] = {
                "fecha_creacion_monitor": hoy,
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
            }
        elif not self.certificado["activacion"].get("fecha_creacion_monitor"):
            self.certificado["activacion"]["fecha_creacion_monitor"] = hoy

    def mostrar(self):
        while True:
            act = self.certificado["activacion"]
            ip_mostrar = act.get("ip_fija") or act.get("ip_final", "")

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}ACTIVACIÓN Y PRUEBAS{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Activación"))
            print()

            print(campo("Fecha creación monitor", act.get('fecha_creacion_monitor', '')))
            print(campo("Tipo IP", act.get('tipo_ip', '')))
            print(campo("IP Fija", ip_mostrar))
            print(campo_bool("Ping OK", act.get('ping_ok', False)))
            print(campo_bool("SSH OK", act.get('ssh_ok', False)))
            print(campo_bool("Datos Visibles", act.get('datos_visibles', False)))
            print(campo_bool("Transmisión OK", act.get('transmision_ok', False)))
            print(campo_bool("Alarmas Activadas", act.get('alarmas_activadas', False)))
            print(campo("Responsable Activación", act.get('responsable_activacion', '')))
            motes_cnt = len(self.certificado.get("motes", []))
            print(campo("Equipos Jennic (motes)", f"{motes_cnt} registrados"))

            print()
            print(separador())
            print()
            print(opcion_menu("E", "Editar datos de activación"))
            print(opcion_menu("M", "Gestionar Equipos Jennic"))
            print(opcion_menu("V", "Volver"))
            print()

            opcion = input(prompt()).strip().upper()

            if opcion == "E":
                self.editar()
            elif opcion == "M":
                from .motes import MotesScreen
                MotesScreen(self.certificado).mostrar()
            elif opcion == "V":
                break
            else:
                print(notificacion_error("Opción inválida"))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def editar(self):
        copia_original = copy.deepcopy(self.certificado["activacion"])
        act = self.certificado["activacion"]

        limpiar_pantalla()
        print()
        print(encabezado_edicion("EDITAR ACTIVACIÓN Y PRUEBAS"))
        print(breadcrumb("Inicio", "Certificado", "Activación", "Editar"))
        print()

        try:
            act["fecha_creacion_monitor"] = pedir_fecha_con_default(
                act.get("fecha_creacion_monitor", ""),
                mensaje="Fecha creación monitor"
            )

            tipo_ip = pedir_tipo_ip(
                act.get("tipo_ip", "")
            )
            act["tipo_ip"] = tipo_ip

            if tipo_ip == "Fija":
                ip_actual = act.get("ip_fija") or act.get("ip_final", "")
                act["ip_fija"] = pedir_ip(
                    "IP Fija",
                    ip_actual,
                    obligatorio=True
                )
                act["ip_final"] = act["ip_fija"]
            else:
                act["ip_fija"] = ""
                act["ip_final"] = ""

            act["ping_ok"] = (
                pedir_opcion_si_no("Ping OK", "Si" if act.get("ping_ok") else "No") == "Si"
            )

            act["ssh_ok"] = (
                pedir_opcion_si_no("SSH OK", "Si" if act.get("ssh_ok") else "No") == "Si"
            )

            act["datos_visibles"] = (
                pedir_opcion_si_no("Datos visibles", "Si" if act.get("datos_visibles") else "No") == "Si"
            )

            act["transmision_ok"] = (
                pedir_opcion_si_no("Transmisión OK", "Si" if act.get("transmision_ok") else "No") == "Si"
            )

            act["alarmas_activadas"] = (
                pedir_opcion_si_no("Alarmas activadas", "Si" if act.get("alarmas_activadas") else "No") == "Si"
            )

            act["responsable_activacion"] = pedir_con_default(
                "Responsable activación",
                act.get("responsable_activacion", "")
            )

            act["estado_final"] = pedir_con_default(
                "Estado final",
                act.get("estado_final", "")
            )

            print(notificacion_exito("Activación actualizada."))

        except CancelarEdicionException:
            self.certificado["activacion"] = copia_original
            print(notificacion_advertencia("Edición cancelada. Se restauraron los datos originales."))
        except GuardarAvanceException:
            print(notificacion_exito("Avance guardado hasta este punto."))
