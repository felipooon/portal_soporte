import copy
from ..utils.input_helpers import (
    pedir_encargado_area,
    pedir_tecnico_visita,
    pedir_empresa,
    pedir_fecha_con_default,
    pedir_numero_con_default,
    pedir_con_default,
    CancelarEdicionException,
    GuardarAvanceException
)
from .ui import (
    limpiar_pantalla, caja, campo, separador, breadcrumb,
    opcion_menu, prompt, encabezado_edicion,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    Color, Icono
)


class DatosGeneralesScreen:

    def __init__(self, certificado: dict):

        self.certificado = certificado

        if "datos_generales" not in self.certificado:

            self.certificado["datos_generales"] = {}

    def mostrar(self):

        while True:

            datos = self.certificado[
                "datos_generales"
            ]

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}DATOS GENERALES{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Datos Generales"))
            print()

            print(campo("Encargado Área", datos.get('encargado_area', '')))
            print(campo("Técnico visita", datos.get('tecnico_visita', '')))
            print(campo("Empresa", datos.get('empresa', '')))
            print(campo("Centro", datos.get('nombre_centro', '')))
            print(campo("Fecha instalación", datos.get('fecha_instalacion', '')))
            print(campo("N° ficha", datos.get('numero_ficha', '')))
            print(campo("Coordenadas", datos.get('coordenadas', '')))
            print(campo("Barrio", datos.get('barrio', '')))
            print(campo("Puerto Patrón", datos.get('puerto_patron', '')))
            print(campo("Correo Centro", datos.get('correo_centro', '')))
            print(campo("Número Centro", datos.get('numero_centro', '')))

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
        copia_original = copy.deepcopy(self.certificado["datos_generales"])
        datos = self.certificado["datos_generales"]

        limpiar_pantalla()
        print()
        print(encabezado_edicion("EDITAR DATOS GENERALES"))
        print(breadcrumb("Inicio", "Certificado", "Datos Generales", "Editar"))
        print()

        try:
            datos["encargado_area"] = (
                pedir_encargado_area(
                    datos.get(
                        "encargado_area",
                        ""
                    )
                )
            )

            datos["tecnico_visita"] = (
                pedir_tecnico_visita(
                    datos[
                        "encargado_area"
                    ],
                    datos.get(
                        "tecnico_visita",
                        ""
                    )
                )
            )

            datos["empresa"] = (
                pedir_empresa(
                    datos.get(
                        "empresa",
                        ""
                    )
                )
            )

            print(
                f"  {Color.DIM}Centro: {datos.get('nombre_centro', '')}{Color.RESET}"
            )
            print(
                f"  {Color.DIM}(No editable){Color.RESET}"
            )
            print()

            datos["fecha_instalacion"] = (
                pedir_fecha_con_default(
                    datos.get(
                        "fecha_instalacion",
                        ""
                    )
                )
            )

            datos["numero_ficha"] = (
                pedir_numero_con_default(
                    "N° ficha",
                    datos.get(
                        "numero_ficha",
                        ""
                    )
                )
            )

            datos["coordenadas"] = pedir_con_default(
                "Coordenadas",
                datos.get("coordenadas", "")
            )

            datos["barrio"] = pedir_con_default(
                "Barrio",
                datos.get("barrio", "")
            )

            datos["puerto_patron"] = pedir_con_default(
                "Puerto Patrón",
                datos.get("puerto_patron", "")
            )

            datos["correo_centro"] = pedir_con_default(
                "Correo del centro",
                datos.get("correo_centro", "")
            )

            datos["numero_centro"] = pedir_con_default(
                "Número del centro",
                datos.get("numero_centro", "")
            )
            print(notificacion_exito("Datos generales actualizados."))

        except CancelarEdicionException:
            self.certificado["datos_generales"] = copia_original
            print(notificacion_advertencia("Edición cancelada. Se restauraron los datos originales."))
        except GuardarAvanceException:
            print(notificacion_exito("Avance guardado hasta este punto."))