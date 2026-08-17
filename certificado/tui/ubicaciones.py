import copy
from certificado.constants.ubicaciones import (
    TIPOS_CON_METRAJE,
    TIPOS_SIN_METRAJE,
    TIPOS_ELEMENTOS
)
from certificado.utils.input_helpers import (
    pedir_con_default,
    pedir_mac,
    pedir_tipo_repuesto,
    input_con_control,
    CancelarEdicionException,
    GuardarAvanceException
)
from .ui import (
    limpiar_pantalla, caja, separador, breadcrumb, campo,
    opcion_menu, prompt, encabezado_edicion, item_lista, texto_vacio,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    Color, Icono
)


class UbicacionesScreen:

    def __init__(self, certificado: dict):

        self.certificado = certificado

        if "ubicaciones" not in self.certificado:
            self.certificado["ubicaciones"] = []

        if "equipos_repuesto" not in self.certificado:
            self.certificado["equipos_repuesto"] = []

    def mostrar(self):

        while True:

            ubicaciones = self.certificado[
                "ubicaciones"
            ]

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}UBICACIONES Y EQUIPOS{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Ubicaciones"))
            print()

            if not ubicaciones:
                print(texto_vacio("No existen ubicaciones registradas."))
            else:
                for indice, ubicacion in enumerate(
                    ubicaciones,
                    start=1
                ):
                    coords = f" ({ubicacion.get('coordenadas', '')})" if ubicacion.get('coordenadas') else ""
                    elems = len(ubicacion.get('elementos', []))
                    detalle = f"({elems} elementos)" if elems else ""
                    print(item_lista(indice, f"{ubicacion.get('nombre', '')}{coords}", detalle))

            print()
            print(separador())
            print()
            print(opcion_menu("A", "Agregar ubicación"))
            print(opcion_menu("X", "Eliminar ubicación"))
            print(opcion_menu("R", "Gestionar Equipos de Repuesto"))
            print(opcion_menu("V", "Volver"))
            print()
            print(f"  {Color.DIM}Tip: Ingrese un número para gestionar una ubicación{Color.RESET}")
            print()

            opcion = input(prompt()).strip().upper()

            if opcion == "A":
                self.agregar_ubicacion()

            elif opcion == "X":
                self.eliminar_ubicacion()

            elif opcion == "R":
                self.gestionar_repuestos()

            elif opcion == "V":
                break

            elif opcion.isdigit():
                indice = int(opcion) - 1
                if 0 <= indice < len(ubicaciones):
                    self.gestionar_ubicacion(indice)
                else:
                    print(notificacion_error("Selección inválida."))
                    input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

            else:
                print(notificacion_error("Opción inválida"))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def agregar_ubicacion(self):

        limpiar_pantalla()
        print()
        print(caja(f"{Color.BOLD}NUEVA UBICACIÓN{Color.RESET}"))
        print(f"  {Color.DIM}Tip: Ingrese ':c' o 'CANCELAR' para anular{Color.RESET}")
        print()

        try:
            nombre = input_con_control(
                "Nombre ubicación: "
            ).strip()

            if not nombre:
                print(notificacion_advertencia("Ubicación cancelada."))
                return

            coordenadas = input_con_control(
                "Coordenadas (Lat Long) [opcional]: "
            ).strip()

            self.certificado[
                "ubicaciones"
            ].append(
                {
                    "nombre": nombre,
                    "coordenadas": coordenadas,
                    "elementos": []
                }
            )

            print(notificacion_exito(f"Ubicación '{nombre}' agregada."))
        except (CancelarEdicionException, GuardarAvanceException):
            print(notificacion_advertencia("Creación de ubicación cancelada."))

    def eliminar_ubicacion(self):

        ubicaciones = self.certificado[
            "ubicaciones"
        ]

        if not ubicaciones:
            print(notificacion_advertencia("No existen ubicaciones."))
            input(f"  {Color.DIM}Presione Enter...{Color.RESET}")
            return

        print()
        for indice, ubicacion in enumerate(
            ubicaciones,
            start=1
        ):
            print(item_lista(indice, ubicacion.get('nombre', '')))

        print()

        seleccion = input(
            prompt("Número a eliminar")
        ).strip()

        if not seleccion.isdigit():
            print(notificacion_error("Selección inválida."))
            return

        indice = int(seleccion) - 1

        if (
            indice < 0
            or indice >= len(
                ubicaciones
            )
        ):
            print(notificacion_error("Selección inválida."))
            return

        nombre = ubicaciones[
            indice
        ][
            "nombre"
        ]

        del ubicaciones[
            indice
        ]

        print(notificacion_exito(f"Ubicación '{nombre}' eliminada."))

    def gestionar_ubicacion(
        self,
        indice: int
    ):

        ubicacion = self.certificado[
            "ubicaciones"
        ][
            indice
        ]

        while True:

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}UBICACIÓN: {ubicacion['nombre'].upper()}{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Ubicaciones", ubicacion['nombre']))
            print()

            elementos = ubicacion[
                "elementos"
            ]

            if not elementos:
                print(texto_vacio("No existen elementos."))
            else:
                for numero, elemento in enumerate(
                    elementos,
                    start=1
                ):
                    print(item_lista(numero, self.formatear_elemento(elemento)))

            print()
            print(separador())
            print()
            print(opcion_menu("A", "Agregar elemento"))
            print(opcion_menu("E", "Editar elemento"))
            print(opcion_menu("X", "Eliminar elemento"))
            print(opcion_menu("V", "Volver"))
            print()

            opcion = input(prompt()).strip().upper()

            if opcion == "A":
                self.agregar_elemento(
                    ubicacion
                )

            elif opcion == "E":
                self.editar_elemento(
                    ubicacion
                )

            elif opcion == "X":
                self.eliminar_elemento(
                    ubicacion
                )

            elif opcion == "V":
                break

            else:
                print(notificacion_error("Opción inválida"))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def agregar_elemento(
        self,
        ubicacion: dict
    ):

        opciones = TIPOS_ELEMENTOS

        limpiar_pantalla()
        print()
        print(caja(f"{Color.BOLD}AGREGAR ELEMENTO{Color.RESET}"))
        print(f"  {Color.DIM}Tip: Ingrese ':c' o 'CANCELAR' para anular{Color.RESET}")
        print()

        try:
            for indice, opcion in enumerate(
                opciones,
                start=1
            ):
                print(f"    {Color.CYAN}{indice}.{Color.RESET} {opcion}")

            print()

            seleccion = input_con_control(
                "Seleccione elemento: "
            ).strip()

            if not seleccion.isdigit():

                return

            indice = int(seleccion) - 1

            if (
                indice < 0
                or indice >= len(opciones)
            ):

                return

            tipo = opciones[indice]

            elemento = {
                "tipo": tipo
            }

            if tipo in TIPOS_CON_METRAJE:

                metraje = input_con_control(
                    "Metraje (m): "
                ).strip()

                if not metraje:

                    return

                elemento[
                    "metraje"
                ] = metraje

            elif tipo == "Otro":

                descripcion = input_con_control(
                    "Descripción: "
                ).strip()

                if not descripcion:

                    return

                elemento[
                    "descripcion"
                ] = descripcion

            es_equipo_jennic = ("jennic" in tipo.lower() or "mote" in tipo.lower() or tipo == "Equipo Jennic")
            if es_equipo_jennic:
                motes = self.certificado.get("motes", [])
                mac = pedir_mac("MAC Address del Equipo Jennic", elemento.get("mac", ""), motes=motes)
                if mac:
                    elemento["mac"] = mac
            else:
                serie = pedir_con_default("N° de Serie físico del sensor [opcional]", elemento.get("numero_serie", ""))
                if serie:
                    elemento["numero_serie"] = serie
                    elemento["serie"] = serie

            ubicacion[
                "elementos"
            ].append(
                elemento
            )

            print(notificacion_exito("Elemento agregado."))
        except (CancelarEdicionException, GuardarAvanceException):
            print(notificacion_advertencia("Alta de elemento cancelada."))

    def eliminar_elemento(
        self,
        ubicacion: dict
    ):

        elementos = ubicacion[
            "elementos"
        ]

        if not elementos:
            print(notificacion_advertencia("No existen elementos."))
            input(f"  {Color.DIM}Presione Enter...{Color.RESET}")
            return

        print()

        for indice, elemento in enumerate(
            elementos,
            start=1
        ):
            print(item_lista(indice, self.formatear_elemento(elemento)))

        print()

        seleccion = input(
            prompt("Número a eliminar")
        ).strip()

        if not seleccion.isdigit():
            print(notificacion_error("Selección inválida."))
            return

        indice = int(seleccion) - 1

        if (
            indice < 0
            or indice >= len(
                elementos
            )
        ):
            print(notificacion_error("Selección inválida."))
            return

        eliminado = elementos.pop(
            indice
        )

        print(notificacion_exito(f"Elemento '{self.formatear_elemento(eliminado)}' eliminado."))

    def editar_elemento(
        self,
        ubicacion: dict
    ):

        elementos = ubicacion[
            "elementos"
        ]

        if not elementos:
            print(notificacion_advertencia("No existen elementos."))
            input(f"  {Color.DIM}Presione Enter...{Color.RESET}")
            return

        print()

        for indice, elemento in enumerate(
            elementos,
            start=1
        ):
            print(item_lista(indice, self.formatear_elemento(elemento)))

        print()

        seleccion = input(
            prompt("Número a editar")
        ).strip()

        if not seleccion.isdigit():

            return

        indice = int(seleccion) - 1

        if (
            indice < 0
            or indice >= len(elementos)
        ):

            return

        elemento = elementos[
            indice
        ]
        copia_elem = copy.deepcopy(elemento)

        limpiar_pantalla()
        print()
        print(encabezado_edicion("EDITAR ELEMENTO"))
        print()

        try:
            if elemento["tipo"] in TIPOS_CON_METRAJE:

                actual = elemento.get(
                    "metraje",
                    ""
                )

                nuevo = input_con_control(
                    f"Metraje [{actual}]: "
                ).strip()

                if nuevo:

                    elemento[
                        "metraje"
                    ] = nuevo

            elif elemento["tipo"] == "Otro":

                actual = elemento.get(
                    "descripcion",
                    ""
                )

                nuevo = input_con_control(
                    f"Descripción [{actual}]: "
                ).strip()

                if nuevo:

                    elemento[
                        "descripcion"
                    ] = nuevo

            tipo_elem = elemento.get("tipo", "")
            es_equipo_jennic = ("jennic" in tipo_elem.lower() or "mote" in tipo_elem.lower() or tipo_elem == "Equipo Jennic")

            if es_equipo_jennic:
                motes = self.certificado.get("motes", [])
                mac_act = elemento.get("mac", "")
                nueva_mac = pedir_mac("MAC Address del Equipo Jennic", mac_act, motes=motes)
                if nueva_mac:
                    elemento["mac"] = nueva_mac
            else:
                serie_act = elemento.get("numero_serie") or elemento.get("serie", "")
                nueva_serie = pedir_con_default("N° de Serie físico del sensor [opcional]", serie_act)
                if nueva_serie:
                    elemento["numero_serie"] = nueva_serie
                    elemento["serie"] = nueva_serie

            print(notificacion_exito("Elemento actualizado."))
        except CancelarEdicionException:
            elementos[indice] = copia_elem
            print(notificacion_advertencia("Edición cancelada. Elemento restaurado."))
        except GuardarAvanceException:
            print(notificacion_exito("Avance guardado hasta este punto."))

    def formatear_elemento(
        self,
        elemento: dict
    ):

        if elemento["tipo"] == "Otro":
            res = elemento.get("descripcion", "")
        elif elemento.get("metraje"):
            res = f"{elemento['tipo']} {elemento['metraje']}m"
        else:
            res = elemento["tipo"]

        mac = elemento.get("mac", "")
        serie = elemento.get("numero_serie") or elemento.get("serie", "")

        extras = []
        if mac:
            extras.append(f"MAC: {mac}")
        if serie:
            extras.append(f"S/N: {serie}")

        if extras:
            res += f" {Color.DIM}({', '.join(extras)}){Color.RESET}"

        return res

    def gestionar_repuestos(self):
        while True:
            repuestos = self.certificado["equipos_repuesto"]
            ub_repuestos = self.certificado.get("ubicacion_repuestos") or ""

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}EQUIPOS DE REPUESTO{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Ubicaciones", "Repuestos"))
            print()

            print(campo("Ubicación Repuestos", ub_repuestos))
            print()

            if not repuestos:
                print(texto_vacio("No existen equipos de repuesto registrados."))
            else:
                for idx, rep in enumerate(repuestos, start=1):
                    tipo = rep.get("tipo", rep.get("descripcion", ""))
                    metraje = rep.get("metraje", "")
                    tipo_str = f"{tipo} {metraje}m" if metraje else tipo
                    es_jennic = ("jennic" in tipo.lower() or "mote" in tipo.lower() or tipo == "Equipo Jennic")

                    if es_jennic:
                        ident = rep.get("mac") or rep.get("identificacion", "")
                        ident_str = f" — MAC: {ident}" if ident else ""
                    else:
                        ident = rep.get("serie") or rep.get("numero_serie") or rep.get("identificacion", "")
                        ident_str = f" — S/N: {ident}" if ident else ""

                    print(item_lista(idx, f"{tipo_str}{ident_str}"))

            print()
            print(separador())
            print()
            print(opcion_menu("U", "Editar ubicación repuestos"))
            print(opcion_menu("A", "Agregar equipo de repuesto"))
            print(opcion_menu("X", "Eliminar equipo de repuesto"))
            print(opcion_menu("V", "Volver"))
            print()

            opc = input(prompt()).strip().upper()

            if opc == "U":
                actual_ub = self.certificado.get("ubicacion_repuestos", "")
                nueva_ub = pedir_con_default("Ubicación de repuestos", actual_ub)
                self.certificado["ubicacion_repuestos"] = nueva_ub
                print(notificacion_exito("Ubicación de repuestos actualizada."))
            elif opc == "A":
                self.agregar_repuesto()
            elif opc == "X":
                self.eliminar_repuesto()
            elif opc == "V":
                break
            else:
                print(notificacion_error("Opción inválida."))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def agregar_repuesto(self):
        limpiar_pantalla()
        print()
        print(caja(f"{Color.BOLD}AGREGAR EQUIPO DE REPUESTO{Color.RESET}"))
        print(f"  {Color.DIM}Tip: Ingrese ':c' o 'CANCELAR' para anular{Color.RESET}")
        print()

        try:
            tipo = pedir_tipo_repuesto()
            cant_str = input_con_control("Cantidad [1]: ").strip()
            cant = int(cant_str) if cant_str.isdigit() and int(cant_str) > 0 else 1

            es_equipo_jennic = ("jennic" in tipo.lower() or "mote" in tipo.lower() or tipo == "Equipo Jennic")

            if not self.certificado.get("ubicacion_repuestos"):
                ub = pedir_con_default("Ubicación de repuestos [opcional]")
                if ub:
                    self.certificado["ubicacion_repuestos"] = ub

            ubicacion = self.certificado.get("ubicacion_repuestos", "")
            motes = self.certificado.get("motes", []) if es_equipo_jennic else []

            if cant == 1:
                if es_equipo_jennic:
                    ident = pedir_mac("MAC Address del Equipo Jennic", "", motes=motes)
                    metraje = ""
                else:
                    ident = pedir_con_default("N° de serie del sensor")
                    metraje = input_con_control("Metraje (m) [opcional]: ").strip()

                rep = {
                    "tipo": tipo,
                    "cant": 1,
                    "cantidad": 1,
                    "descripcion": tipo,
                    "metraje": metraje,
                    "identificacion": ident,
                    "serie": ident if not es_equipo_jennic else "",
                    "mac": ident if es_equipo_jennic else "",
                    "ubicacion": ubicacion
                }
                self.certificado["equipos_repuesto"].append(rep)
                print(notificacion_exito(f"Equipo de repuesto '{tipo}' registrado."))
            else:
                lbl = "MAC Address" if es_equipo_jennic else "N° de serie y metraje"
                print(f"\n  {Color.DIM}Ingrese datos de ({lbl}) para cada uno de los {cant} equipos:{Color.RESET}")

                for i in range(1, cant + 1):
                    if es_equipo_jennic:
                        ident = pedir_mac(f"MAC Address [{i}° equipo]", "", motes=motes)
                        metraje = ""
                    else:
                        ident = pedir_con_default(f"N° de serie [{i}° sensor]")
                        metraje = input_con_control(f"Metraje (m) [{i}° sensor]: ").strip()

                    rep = {
                        "tipo": tipo,
                        "cant": 1,
                        "cantidad": 1,
                        "descripcion": tipo,
                        "metraje": metraje,
                        "identificacion": ident,
                        "serie": ident if not es_equipo_jennic else "",
                        "mac": ident if es_equipo_jennic else "",
                        "ubicacion": ubicacion
                    }
                    self.certificado["equipos_repuesto"].append(rep)

                print(notificacion_exito(f"{cant} equipos de repuesto '{tipo}' registrados individualmente."))

        except (CancelarEdicionException, GuardarAvanceException):
            print(notificacion_advertencia("Registro de repuesto cancelado."))

    def eliminar_repuesto(self):
        repuestos = self.certificado["equipos_repuesto"]
        if not repuestos:
            print(notificacion_advertencia("No hay repuestos registrados."))
            input(f"  {Color.DIM}Presione Enter...{Color.RESET}")
            return

        print()
        for idx, rep in enumerate(repuestos, start=1):
            tipo = rep.get("tipo", rep.get("descripcion", ""))
            cant = rep.get("cant", rep.get("cantidad", 1))
            print(item_lista(idx, tipo))

        print()
        sel = input(prompt("Número a eliminar")).strip()
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(repuestos):
                eliminado = repuestos.pop(idx)
                print(notificacion_exito(f"Repuesto '{eliminado.get('tipo', '')}' eliminado."))
            else:
                print(notificacion_error("Selección inválida."))
        else:
            print(notificacion_error("Selección inválida."))