import copy
from certificado.utils.input_helpers import (
    pedir_categoria_pc,
    pedir_sistema_operativo,
    pedir_mac,
    pedir_ip,
    pedir_con_default,
    input_con_control,
    CancelarEdicionException,
    GuardarAvanceException
)
from .ui import (
    limpiar_pantalla, caja, campo, separador, breadcrumb,
    opcion_menu, prompt, encabezado_edicion,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    Color, Icono
)


class InfraestructuraScreen:

    def __init__(self, certificado: dict):

        self.certificado = certificado

        if "infraestructura" not in self.certificado:

            self.certificado["infraestructura"] = {}

    def mostrar(self):

        while True:

            infraestructura = self.certificado[
                "infraestructura"
            ]

            ip_vpn = infraestructura.get("ip_vpn") or self.certificado.get("acceso_remoto", {}).get("tun0") or self.certificado.get("activacion", {}).get("vpn_tun0") or ""

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}INFRAESTRUCTURA{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Infraestructura"))
            print()

            print(campo("Categoría", infraestructura.get('categoria', '')))
            print(campo("Marca", infraestructura.get('marca', '')))
            print(campo("Modelo", infraestructura.get('modelo', '')))
            print(campo("Serie", infraestructura.get('serie', '')))
            print(campo("MAC Ethernet", infraestructura.get('mac_ethernet', '')))
            print(campo("ID PC / AnyDesk", infraestructura.get('pc_id', '')))
            print(campo("Contraseña PC", infraestructura.get('pc_password', '')))
            print(campo("Ubicación PC", infraestructura.get('ubicacion_pc', '')))
            print(campo("Sistema Operativo", infraestructura.get('sistema_operativo', '')))
            print(campo("Conectividad", infraestructura.get('conectividad', '')))
            print(campo("IP VPN (tun0)", ip_vpn))

            if infraestructura.get("conectividad") == "Cableada":
                print(campo("Switch", infraestructura.get('switch', '')))
                print(campo("Puerto", infraestructura.get('puerto', '')))

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
        copia_original = copy.deepcopy(self.certificado["infraestructura"])
        infraestructura = self.certificado["infraestructura"]

        limpiar_pantalla()
        print()
        print(encabezado_edicion("EDITAR INFRAESTRUCTURA"))
        print(breadcrumb("Inicio", "Certificado", "Infraestructura", "Editar"))
        print()

        try:
            cat_act = infraestructura.get("categoria", "")
            cat_sel = pedir_categoria_pc(cat_act)
            infraestructura["categoria"] = cat_sel

            if cat_sel == "Notebook":
                if not infraestructura.get("marca"):
                    infraestructura["marca"] = "Dell Inc."
                if not infraestructura.get("modelo"):
                    infraestructura["modelo"] = "Vostro 3405"

                con_act = infraestructura.get("conectividad", "")
                print()
                if con_act:
                    print(f"  {Color.DIM}Conectividad actual: {con_act}{Color.RESET}")
                print(f"  {Color.BOLD}Conectividad{Color.RESET}")
                print(f"    {Color.CYAN}1.{Color.RESET} Wifi")
                print(f"    {Color.CYAN}2.{Color.RESET} Cableada")
                print()

                prompt_con = f"Seleccione conectividad [{con_act}]: " if con_act else "Seleccione conectividad: "
                opcion_conectividad = input_con_control(prompt_con).strip()

                if not opcion_conectividad and con_act:
                    opcion_conectividad = "1" if con_act == "Wifi" else "2" if con_act == "Cableada" else ""

                if opcion_conectividad in ("1", "Wifi"):
                    infraestructura["conectividad"] = "Wifi"
                    infraestructura["switch"] = ""
                    infraestructura["puerto"] = ""

                elif opcion_conectividad in ("2", "Cableada"):
                    infraestructura["conectividad"] = "Cableada"
                    infraestructura["switch"] = self.pedir_switch(
                        infraestructura.get("switch", "")
                    )
                    infraestructura["puerto"] = pedir_con_default(
                        "Puerto",
                        infraestructura.get("puerto", "")
                    )

            elif cat_sel == "RPI":
                infraestructura["marca"] = "RPI"
                infraestructura["modelo"] = "RPI"
                infraestructura["conectividad"] = "BAM"
                infraestructura["switch"] = ""
                infraestructura["puerto"] = ""

                return

            print()

            infraestructura["serie"] = pedir_con_default(
                "Serie",
                infraestructura.get("serie", "")
            )

            infraestructura["mac_ethernet"] = pedir_mac(
                "MAC Ethernet",
                infraestructura.get("mac_ethernet", "")
            )

            infraestructura["pc_id"] = pedir_con_default(
                "ID PC / AnyDesk",
                infraestructura.get("pc_id", "")
            )

            infraestructura["pc_password"] = pedir_con_default(
                "Contraseña PC",
                infraestructura.get("pc_password", "")
            )

            infraestructura["ubicacion_pc"] = pedir_con_default(
                "Ubicación PC",
                infraestructura.get("ubicacion_pc", "Pontón")
            )

            infraestructura[
                "sistema_operativo"
            ] = pedir_sistema_operativo(
                infraestructura.get("sistema_operativo", "")
            )

            ip_vpn_act = infraestructura.get("ip_vpn") or self.certificado.get("acceso_remoto", {}).get("tun0", "")
            nueva_vpn = pedir_ip("IP VPN (tun0)", ip_vpn_act, obligatorio=False)
            if nueva_vpn:
                infraestructura["ip_vpn"] = nueva_vpn
                if "acceso_remoto" not in self.certificado:
                    self.certificado["acceso_remoto"] = {}
                self.certificado["acceso_remoto"]["tun0"] = nueva_vpn

            print(notificacion_exito("Infraestructura actualizada."))

        except CancelarEdicionException:
            self.certificado["infraestructura"] = copia_original
            print(notificacion_advertencia("Edición cancelada. Se restauraron los datos originales."))
        except GuardarAvanceException:
            print(notificacion_exito("Avance guardado hasta este punto."))

    def pedir_switch(self, actual: str = "") -> str:
        print()
        if actual:
            print(f"  {Color.DIM}Switch actual: {actual}{Color.RESET}")
        print(f"    {Color.CYAN}1.{Color.RESET} Fortinet")
        print(f"    {Color.CYAN}2.{Color.RESET} USW")
        print(f"    {Color.CYAN}3.{Color.RESET} Linksys")
        print(f"    {Color.CYAN}4.{Color.RESET} Otro")
        print()

        prompt_sw = f"Seleccione Switch [{actual}]: " if actual else "Seleccione Switch: "
        opcion = input_con_control(prompt_sw).strip()

        if not opcion and actual:
            return actual

        if opcion == "1":
            return "Fortinet"
        if opcion == "2":
            return "USW"
        if opcion == "3":
            return "Linksys"
        if opcion == "4":
            return input_con_control("Escriba el nombre del Switch: ").strip()

        if opcion and not opcion.isdigit():
            return opcion

        return actual or "Fortinet"