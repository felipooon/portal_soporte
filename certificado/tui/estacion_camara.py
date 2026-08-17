import copy
from ..utils.input_helpers import (
    pedir_opcion_si_no,
    pedir_tipo_ip,
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


class EstacionCamaraScreen:

    def __init__(self, certificado: dict):

        self.certificado = certificado

        if "estacion_camara" not in self.certificado:

            self.certificado["estacion_camara"] = {
                "camara_instalada": "",
                "modelo_camara": "",
                "tipo_ip_camara": "",
                "ip_fija_camara": "",
                "conexion_camara": "",
                "ubicacion_camara": "",
                "estacion_instalada": "",
                "modelo_estacion": "",
                "region_davis": "",
                "ubicacion_estacion": "",
                "switch_poe": "",
                "modelo_switch": "",
                "ubicacion_switch": ""
            }

    def mostrar(self):

        while True:

            datos = self.certificado[
                "estacion_camara"
            ]

            tipo_ip_cam = datos.get("tipo_ip_camara", "")
            ip_cam = datos.get("ip_fija_camara", "")
            if tipo_ip_cam == "Fija" and ip_cam:
                det_ip = f"Fija ({ip_cam})"
            elif tipo_ip_cam:
                det_ip = tipo_ip_cam
            elif ip_cam:
                det_ip = f"Fija ({ip_cam})"
            else:
                det_ip = ""

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}EST. METEO. / CÁMARA / SWITCH POE{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Est. Meteo./Cámara"))
            print()

            # Sección Cámara
            print(f"  {Color.BOLD}{Color.CYAN}Cámara{Color.RESET}")
            print(campo("Cámara instalada", datos.get('camara_instalada', '')))
            print(campo("Modelo cámara", datos.get('modelo_camara', '')))
            print(campo("IP cámara", det_ip))
            print(campo("Conexión cámara", datos.get('conexion_camara', '')))
            print(campo("Ubicación cámara", datos.get('ubicacion_camara', '')))

            print()

            # Sección Estación
            print(f"  {Color.BOLD}{Color.CYAN}Estación Meteorológica{Color.RESET}")
            print(campo("Estación instalada", datos.get('estacion_instalada', '')))
            print(campo("Modelo estación", datos.get('modelo_estacion', '')))
            print(campo("Región Davis", datos.get('region_davis', '')))
            print(campo("Ubicación estación", datos.get('ubicacion_estacion', '')))

            print()

            # Sección Switch PoE
            print(f"  {Color.BOLD}{Color.CYAN}Switch PoE{Color.RESET}")
            print(campo("Switch PoE", datos.get('switch_poe', '')))
            print(campo("Modelo Switch", datos.get('modelo_switch', '')))
            print(campo("Ubicación Switch", datos.get('ubicacion_switch', '')))

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
        copia_original = copy.deepcopy(self.certificado["estacion_camara"])
        datos = self.certificado["estacion_camara"]

        limpiar_pantalla()
        print()
        print(encabezado_edicion("EDITAR EST. METEO. / CÁMARA / SWITCH POE"))
        print(breadcrumb("Inicio", "Certificado", "Est. Meteo./Cámara", "Editar"))
        print()

        try:
            datos["camara_instalada"] = (
                pedir_opcion_si_no(
                    "Cámara instalada",
                    datos.get(
                        "camara_instalada",
                        ""
                    )
                )
            )

            if datos["camara_instalada"] == "Si":

                datos["modelo_camara"] = (
                    self.pedir_modelo_camara(
                        datos.get(
                            "modelo_camara",
                            ""
                        )
                    )
                )

                tipo_ip_cam = pedir_tipo_ip(
                    datos.get("tipo_ip_camara", "Fija")
                )
                datos["tipo_ip_camara"] = tipo_ip_cam

                if tipo_ip_cam == "Fija":
                    ip_actual = datos.get("ip_fija_camara", "")
                    if ip_actual == "Dinámica":
                        ip_actual = ""
                    datos["ip_fija_camara"] = pedir_ip(
                        "IP Fija Cámara",
                        ip_actual,
                        obligatorio=True
                    )
                else:
                    datos["ip_fija_camara"] = ""

                datos["conexion_camara"] = (
                    self.pedir_conexion_camara(
                        datos.get(
                            "conexion_camara",
                            ""
                        )
                    )
                )

                datos["ubicacion_camara"] = pedir_con_default(
                    "Ubicación cámara",
                    datos.get("ubicacion_camara", "Pontón")
                )

            else:

                datos["modelo_camara"] = ""
                datos["tipo_ip_camara"] = ""
                datos["ip_fija_camara"] = ""
                datos["conexion_camara"] = ""
                datos["ubicacion_camara"] = ""

            print()

            datos["estacion_instalada"] = (
                pedir_opcion_si_no(
                    "Estación meteorológica instalada",
                    datos.get(
                        "estacion_instalada",
                        ""
                    )
                )
            )

            if datos["estacion_instalada"] == "Si":

                datos["modelo_estacion"] = (
                    self.pedir_modelo_estacion(
                        datos.get(
                            "modelo_estacion",
                            ""
                        )
                    )
                )

                if datos["modelo_estacion"] == "Davis":

                    datos["region_davis"] = (
                        self.pedir_region_davis(
                            datos.get(
                                "region_davis",
                                ""
                            )
                        )
                    )

                else:

                    datos["region_davis"] = ""

                datos["ubicacion_estacion"] = pedir_con_default(
                    "Ubicación estación meteorológica",
                    datos.get("ubicacion_estacion", "Pontón")
                )

            else:

                datos["modelo_estacion"] = ""
                datos["region_davis"] = ""
                datos["ubicacion_estacion"] = ""

            print()

            # Lógica inteligente para evitar redundancia con la cámara
            conexion_cam = datos.get("conexion_camara", "")

            if conexion_cam == "Switch PoE":
                datos["switch_poe"] = "Si"
                datos["modelo_switch"] = pedir_con_default(
                    "Modelo Switch PoE",
                    datos.get("modelo_switch") or "DS-3E0105P-E(B)"
                )
                datos["ubicacion_switch"] = pedir_con_default(
                    "Ubicación Switch PoE",
                    datos.get("ubicacion_switch", "Pontón")
                )
            else:
                datos["switch_poe"] = pedir_opcion_si_no(
                    "Switch PoE instalado",
                    datos.get("switch_poe", "No")
                )

                if datos["switch_poe"] == "Si":
                    datos["modelo_switch"] = pedir_con_default(
                        "Modelo Switch PoE",
                        datos.get("modelo_switch") or "DS-3E0105P-E(B)"
                    )
                    datos["ubicacion_switch"] = pedir_con_default(
                        "Ubicación Switch PoE",
                        datos.get("ubicacion_switch", "Pontón")
                    )
                else:
                    datos["modelo_switch"] = ""
                    datos["ubicacion_switch"] = ""

            print(notificacion_exito("Estación / cámara / switch PoE actualizados."))

        except CancelarEdicionException:
            self.certificado["estacion_camara"] = copia_original
            print(notificacion_advertencia("Edición cancelada. Se restauraron los datos originales."))
        except GuardarAvanceException:
            print(notificacion_exito("Avance guardado hasta este punto."))

    def pedir_modelo_camara(
        self,
        actual
    ):

        print()
        print(f"  {Color.DIM}Modelo actual: {actual}{Color.RESET}")
        print()
        print(f"    {Color.CYAN}1.{Color.RESET} Domo")
        print(f"    {Color.CYAN}2.{Color.RESET} Bala")
        print()

        while True:

            opcion = input_con_control(
                "Seleccione modelo: "
            )

            if opcion == "1":
                return "Domo"

            if opcion == "2":
                return "Bala"

            print(notificacion_error("Opción inválida"))

    def pedir_conexion_camara(
        self,
        actual
    ):

        print()
        print(f"  {Color.DIM}Conexión actual: {actual}{Color.RESET}")
        print()
        print(f"    {Color.CYAN}1.{Color.RESET} Switch PoE")
        print(f"    {Color.CYAN}2.{Color.RESET} Directa PC")
        print(f"    {Color.CYAN}3.{Color.RESET} PoE + HUB")
        print()

        while True:

            opcion = input_con_control(
                "Seleccione conexión: "
            )

            if opcion == "1":
                return "Switch PoE"

            if opcion == "2":
                return "Directa PC"

            if opcion == "3":
                return "PoE + HUB"

            print(notificacion_error("Opción inválida"))

    def pedir_modelo_estacion(
        self,
        actual
    ):

        print()
        print(f"  {Color.DIM}Modelo actual: {actual}{Color.RESET}")
        print()
        print(f"    {Color.CYAN}1.{Color.RESET} Davis")
        print(f"    {Color.CYAN}2.{Color.RESET} AirMar")
        print()

        while True:

            opcion = input_con_control(
                "Seleccione modelo: "
            )

            if opcion == "1":
                return "Davis"

            if opcion == "2":
                return "AirMar"

            print(notificacion_error("Opción inválida"))

    def pedir_region_davis(
        self,
        actual
    ):

        print()
        print(f"  {Color.DIM}Región actual: {actual}{Color.RESET}")
        print()
        print(f"    {Color.CYAN}1.{Color.RESET} US")
        print(f"    {Color.CYAN}2.{Color.RESET} EU")
        print()

        while True:

            opcion = input_con_control(
                "Seleccione región: "
            )

            if opcion == "1":
                return "US"

            if opcion == "2":
                return "EU"

            print(notificacion_error("Opción inválida"))