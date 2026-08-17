import copy
from ..utils.input_helpers import (
    pedir_opcion_si_no,
    pedir_con_default,
    pedir_mac,
    pedir_tipo_antena,
    CancelarEdicionException,
    GuardarAvanceException
)
from .ui import (
    limpiar_pantalla, caja, campo, separador, breadcrumb,
    opcion_menu, prompt, encabezado_edicion, encabezado_pegar,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    notificacion_info, Color, Icono
)


class MonitoreoAbioticoScreen:

    def __init__(self, certificado: dict):

        self.certificado = certificado

        if "monitoreo_abiotico" not in self.certificado:

            self.certificado[
                "monitoreo_abiotico"
            ] = {
                "instalado": "",
                "version": "",
                "mac": "",
                "panid": "",
                "tipo_antena": "",
                "ubicacion_antena": ""
            }

    def mostrar(self):
        while True:
            datos = self.certificado[
                "monitoreo_abiotico"
            ]

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}MONITOREO ABIÓTICO{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Monitoreo Abiótico"))
            print()

            print(campo("Instalado", datos.get('instalado', '')))
            print(campo("Tipo Antena", datos.get('tipo_antena', '')))
            print(campo("Ubicación Antena", datos.get('ubicacion_antena', '')))
            print(campo("Versión", datos.get('version', '')))
            print(campo("MAC", datos.get('mac', '')))
            print(campo("PanID", datos.get('panid', '')))

            print()
            print(separador())
            print()
            print(opcion_menu("E", "Editar"))
            print(opcion_menu("P", "Pegar salida de 'cmd status'"))
            print(opcion_menu("V", "Volver"))
            print()

            opcion = input(prompt()).strip().upper()

            if opcion == "E":
                self.editar()
            elif opcion == "P":
                self.pegar_cmd_status()
            elif opcion == "V":
                break
            else:
                print(notificacion_error("Opción inválida"))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def pegar_cmd_status(self):
        limpiar_pantalla()
        print()

        instrucciones = [
            "Copie y pegue la salida de la consola.",
            "Ingrese 'FIN' o presione Enter dos veces al terminar.",
        ]
        print(encabezado_pegar("PEGAR SALIDA DE 'cmd status'", instrucciones))
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

        if res["exito"]:
            print(notificacion_exito("Datos de antena actualizados desde 'cmd status':"))
            for c in res["resumen"]:
                print(f"    {Color.DIM}{Icono.ARROW} {c}{Color.RESET}")
        else:
            print(notificacion_error("No se pudieron extraer datos de 'cmd status'."))

        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")

    def editar(self):
        copia_original = copy.deepcopy(self.certificado["monitoreo_abiotico"])
        datos = self.certificado["monitoreo_abiotico"]

        limpiar_pantalla()
        print()
        print(encabezado_edicion("EDITAR MONITOREO ABIÓTICO"))
        print(breadcrumb("Inicio", "Certificado", "Monitoreo Abiótico", "Editar"))
        print()

        try:
            datos["instalado"] = (
                pedir_opcion_si_no(
                    "Monitoreo abiótico instalado",
                    datos.get(
                        "instalado",
                        ""
                    )
                )
            )

            if datos["instalado"] == "No":
                datos["version"] = ""
                datos["mac"] = ""
                datos["panid"] = ""
                datos["tipo_antena"] = ""
                datos["ubicacion_antena"] = ""
                print(notificacion_exito("Monitoreo abiótico marcado como no instalado."))
                return

            print()
            datos["tipo_antena"] = pedir_tipo_antena(
                datos.get("tipo_antena", "Outdoor")
            )

            datos["ubicacion_antena"] = pedir_con_default(
                "Ubicación Antena",
                datos.get("ubicacion_antena", "Púlpito")
            )

            datos["version"] = (
                pedir_con_default(
                    "Versión",
                    datos.get(
                        "version",
                        ""
                    )
                )
            )

            datos["mac"] = (
                pedir_mac(
                    "MAC",
                    datos.get(
                        "mac",
                        ""
                    )
                )
            )

            datos["panid"] = (
                pedir_con_default(
                    "PanID",
                    datos.get(
                        "panid",
                        ""
                    )
                )
            )
            print(notificacion_exito("Monitoreo abiótico actualizado."))

        except CancelarEdicionException:
            self.certificado["monitoreo_abiotico"] = copia_original
            print(notificacion_advertencia("Edición cancelada. Se restauraron los datos originales."))
        except GuardarAvanceException:
            print(notificacion_exito("Avance guardado hasta este punto."))