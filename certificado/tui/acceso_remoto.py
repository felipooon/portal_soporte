import copy
from ..utils.input_helpers import (
    pedir_protocolo,
    pedir_puerto_server,
    pedir_con_default,
    pedir_ip,
    CancelarEdicionException,
    GuardarAvanceException
)
from .ui import (
    limpiar_pantalla, caja, campo, separador, breadcrumb,
    opcion_menu, prompt, encabezado_edicion,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    Color, Icono
)


class AccesoRemotoScreen:

    def __init__(self, certificado: dict):
        self.certificado = certificado
        if "acceso_remoto" not in self.certificado:
            self.certificado["acceso_remoto"] = {}

    def mostrar(self):
        while True:
            acceso = self.certificado[
                "acceso_remoto"
            ]
            host = acceso.get("hostserver") or acceso.get("host_server") or "dataweb.innovex.cl"
            puerto = acceso.get("puerto_server") or "8888"

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}ACCESO REMOTO{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Acceso Remoto"))
            print()

            print(campo("Protocolo", acceso.get('protocolo', '')))
            print(campo("Tun0", acceso.get('tun0', '')))
            print(campo("IP Fija", acceso.get('ip_fija', '')))
            print(campo("Host Server", host))
            print(campo("Puerto Server", puerto))

            print()
            print(separador())
            print()
            print(opcion_menu("E", "Editar"))
            print(opcion_menu("V", "Volver"))
            print()

            opcion = input(prompt()).strip().upper()

            if opcion == "E":

                self.editar()

            elif opcion == "V":
                break

            else:
                print(notificacion_error("Opción inválida"))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def editar(self):
        copia_original = copy.deepcopy(self.certificado["acceso_remoto"])
        acceso = self.certificado["acceso_remoto"]
        protocolo_anterior = acceso.get("protocolo", "")

        limpiar_pantalla()
        print()
        print(encabezado_edicion("EDITAR ACCESO REMOTO"))
        print(breadcrumb("Inicio", "Certificado", "Acceso Remoto", "Editar"))
        print()

        try:
            acceso["protocolo"] = (
                pedir_protocolo(
                    protocolo_anterior
                )
            )

            protocolo = acceso["protocolo"]

            if protocolo != protocolo_anterior:
                if (
                    protocolo_anterior == "OpenVPN"
                    and protocolo != "OpenVPN"
                ):
                    acceso["tun0"] = ""
                elif (
                    protocolo_anterior != "OpenVPN"
                    and protocolo == "OpenVPN"
                ):
                    acceso["ip_fija"] = ""

            print()

            if protocolo == "OpenVPN":
                acceso["tun0"] = (
                    pedir_ip(
                        "Tun0",
                        acceso.get("tun0", ""),
                        obligatorio=True
                    )
                )

                acceso["ip_fija"] = (
                    pedir_ip(
                        "IP Fija",
                        acceso.get("ip_fija", ""),
                        obligatorio=False
                    )
                )
            else:
                acceso["ip_fija"] = (
                    pedir_ip(
                        "IP Fija",
                        acceso.get("ip_fija", ""),
                        obligatorio=True
                    )
                )

                acceso["tun0"] = (
                    pedir_ip(
                        "Tun0",
                        acceso.get("tun0", ""),
                        obligatorio=False
                    )
                )

            host_actual = acceso.get("hostserver") or acceso.get("host_server") or "dataweb.innovex.cl"
            acceso["hostserver"] = pedir_con_default("Host Server / Servidor", host_actual)

            puerto_actual = acceso.get("puerto_server") or "8888"
            acceso["puerto_server"] = pedir_puerto_server(puerto_actual)
            print(notificacion_exito("Acceso remoto actualizado."))

        except CancelarEdicionException:
            self.certificado["acceso_remoto"] = copia_original
            print(notificacion_advertencia("Edición cancelada. Se restauraron los datos originales."))
        except GuardarAvanceException:
            print(notificacion_exito("Avance guardado hasta este punto."))