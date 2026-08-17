import copy
import re
from datetime import datetime
from ..constants.personal import (
    ENCARGADOS
)
from ..constants.empresas import (
    EMPRESAS
)
from ..tui.ui import (
    Color, Icono, opcion_menu, prompt, campo,
    notificacion_error, notificacion_advertencia, notificacion_exito,
    encabezado_tabla, fila_tabla, separador
)


class CancelarEdicionException(Exception):
    """Excepción para cancelar la edición sin guardar cambios."""
    pass


class GuardarAvanceException(Exception):
    """Excepción para posponer/guardar el avance realizado hasta el momento."""
    pass


def input_con_control(prompt_str: str) -> str:
    valor = input(prompt_str).strip()
    val_upper = valor.upper()
    if val_upper in (":C", ":CANCELAR", "CANCELAR", "CANCEL", "ABORTAR", "C"):
        raise CancelarEdicionException()
    if val_upper in (":G", ":GUARDAR", ":P", "POSPONER", "GUARDAR", "G"):
        raise GuardarAvanceException()
    return valor


OPCIONES_SO = [
    "Ubuntu 20.04 LTS",
    "Ubuntu 22.04 LTS",
    "Ubuntu 24.04 LTS"
]

OPCIONES_REPUESTO = [
    "Equipo Jennic",
    "Sensor Integrado",
    "Sensor Óptico",
    "Sensor Conductividad"
]

OPCIONES_ANTENA = [
    "Outdoor",
    "Indoor"
]


def pedir_tipo_antena(actual: str = "") -> str:
    while True:
        print()
        if actual:
            print(campo("Tipo de Antena actual", actual))
            print()
        print(opcion_menu("1", "Outdoor"))
        print(opcion_menu("2", "Indoor"))
        print()
        opc = input_con_control(prompt("Seleccione Tipo de Antena"))
        if not opc and actual in OPCIONES_ANTENA:
            return actual
        if opc == "1":
            return "Outdoor"
        if opc == "2":
            return "Indoor"
        print(notificacion_error("Opción inválida. Seleccione 1 o 2."))


def es_ip_valida(ip: str) -> bool:
    partes = ip.split(".")
    if len(partes) != 4:
        return False
    for p in partes:
        if not p.isdigit() or not (0 <= int(p) <= 255):
            return False
    return True


def pedir_ip(
    mensaje: str,
    actual: str = "",
    obligatorio: bool = False
) -> str:
    while True:
        lbl = f"{mensaje} {Color.DIM}[{actual}]{Color.RESET}" if actual else mensaje
        valor = input_con_control(prompt(lbl))
        if not valor:
            if actual:
                return actual
            if not obligatorio:
                return ""
            print(notificacion_error("Este campo es obligatorio."))
            continue
        if es_ip_valida(valor):
            return valor
        print(notificacion_error("Formato IP inválido. Debe ser de la forma xx.xx.xx.xx (ej: 10.9.6.109)."))


def es_mac_valida(mac: str) -> bool:
    partes = mac.split(":")
    if len(partes) not in (4, 6):
        return False
    for p in partes:
        if len(p) != 2 or not all(c in "0123456789ABCDEF" for c in p):
            return False
    return True


def pedir_mac(
    mensaje: str,
    actual: str = "",
    obligatorio: bool = False,
    motes: list[dict] | None = None
) -> str:
    if motes:
        print()
        print(f"  {Color.BOLD}{Color.CYAN}--- Motes detectados en 'cmd motes' ---{Color.RESET}")
        print(encabezado_tabla(("N°", 4), ("MAC Address", 20), ("Asociación / Nombre", 30)))
        for idx, m in enumerate(motes, start=1):
            mac = m.get("mac", "")
            asoc = m.get("asociacion") or m.get("name") or f"Mote {m.get('mote', idx)}"
            print(fila_tabla((str(idx), 4), (mac, 20), (asoc, 30)))
        print(separador())

    while True:
        lbl = f"{mensaje} {Color.DIM}[{actual}]{Color.RESET}" if actual else mensaje
        valor = input_con_control(prompt(lbl)).strip().upper()
        if not valor:
            if actual:
                return actual.upper()
            if not obligatorio:
                return ""
            print(notificacion_error("Este campo es obligatorio."))
            continue

        if valor.isdigit() and motes:
            idx = int(valor) - 1
            if 0 <= idx < len(motes):
                mac_elegida = motes[idx].get("mac", "").upper()
                print(notificacion_exito(f"MAC seleccionada de motes: {mac_elegida}"))
                return mac_elegida

        if es_mac_valida(valor):
            return valor
        print(notificacion_error("Formato MAC inválido. Seleccione un número del listado o ingrese XX:XX:XX:XX."))


def pedir_sistema_operativo(actual: str = "") -> str:
    while True:
        print()
        if actual:
            print(campo("Sistema Operativo actual", actual))
            print()
        for idx, so in enumerate(OPCIONES_SO, start=1):
            print(opcion_menu(str(idx), so))
        print()
        opc = input_con_control(prompt("Seleccione Sistema Operativo"))
        if not opc and actual in OPCIONES_SO:
            return actual
        if opc in ("1", "2", "3"):
            return OPCIONES_SO[int(opc) - 1]
        print(notificacion_error("Opción inválida. Seleccione 1, 2 o 3."))


def pedir_tipo_ip(actual: str = "") -> str:
    while True:
        print()
        if actual:
            print(campo("Tipo IP actual", actual))
            print()
        print(opcion_menu("1", "Fija"))
        print(opcion_menu("2", "Dinámica"))
        print()
        opc = input_con_control(prompt("Seleccione Tipo IP"))
        if not opc and actual in ("Fija", "Dinámica"):
            return actual
        if opc == "1":
            return "Fija"
        if opc == "2":
            return "Dinámica"
        print(notificacion_error("Opción inválida. Seleccione 1 o 2."))


def pedir_tipo_repuesto(actual: str = "") -> str:
    while True:
        print()
        if actual:
            print(campo("Tipo actual", actual))
            print()
        for idx, t in enumerate(OPCIONES_REPUESTO, start=1):
            print(opcion_menu(str(idx), t))
        print()
        opc = input_con_control(prompt("Seleccione Tipo de Repuesto"))
        if not opc and actual in OPCIONES_REPUESTO:
            return actual
        if opc.isdigit():
            idx = int(opc) - 1
            if 0 <= idx < len(OPCIONES_REPUESTO):
                return OPCIONES_REPUESTO[idx]
        print(notificacion_error("Opción inválida."))


def pedir_obligatorio(
    mensaje: str,
    actual: str = ""
) -> str:
    while True:
        lbl = f"{mensaje} {Color.DIM}[{actual}]{Color.RESET}" if actual else mensaje
        valor = input_con_control(prompt(lbl))
        if valor:
            return valor
        if actual:
            return actual
        print(notificacion_error("Este campo es obligatorio."))


def pedir_nombre(
    mensaje: str
) -> str:
    return pedir_obligatorio(mensaje).title()


def pedir_numero_con_default(
    mensaje: str,
    valor_actual: str
) -> str:
    while True:
        lbl = f"{mensaje} {Color.DIM}[{valor_actual}]{Color.RESET}" if valor_actual else mensaje
        valor = input_con_control(prompt(lbl))
        if not valor:
            return valor_actual
        if valor.isdigit():
            return valor
        print(notificacion_error("Debe ingresar solamente números."))


def pedir_numero(
    mensaje: str
) -> str:
    while True:
        valor = input_con_control(prompt(mensaje))
        if valor.isdigit():
            return valor
        print(notificacion_error("Debe ingresar solamente números."))


def pedir_con_default(
    mensaje: str,
    actual: str = ""
) -> str:
    lbl = f"{mensaje} {Color.DIM}[{actual}]{Color.RESET}" if actual else mensaje
    valor = input_con_control(prompt(lbl))
    if valor:
        return valor
    return actual


def pedir_nombre_con_default(
    mensaje: str,
    valor_actual: str
) -> str:
    lbl = f"{mensaje} {Color.DIM}[{valor_actual}]{Color.RESET}" if valor_actual else mensaje
    nuevo = input_con_control(prompt(lbl))
    if not nuevo:
        return valor_actual
    return nuevo.title()


def pedir_fecha_con_default(
    valor_actual: str = "",
    mensaje: str = "Fecha instalación"
) -> str:
    if not valor_actual:
        valor_actual = datetime.now().strftime("%d/%m/%Y")

    while True:
        lbl = f"{mensaje} {Color.DIM}[{valor_actual}]{Color.RESET}"
        fecha = input_con_control(prompt(lbl))
        if not fecha:
            return valor_actual
        try:
            datetime.strptime(fecha, "%d/%m/%Y")
            return fecha
        except ValueError:
            print(notificacion_error("Formato inválido. Use dd/mm/aaaa"))


def pedir_categoria_pc(
    actual: str = ""
) -> str:
    opciones = {
        "1": "Notebook",
        "2": "RPI"
    }

    while True:
        print()
        if actual:
            print(campo("Categoría actual", actual))
            print()

        print(opcion_menu("1", "Notebook"))
        print(opcion_menu("2", "RPI"))
        print()

        opcion = input_con_control(prompt("Seleccione categoría")).strip()

        if not opcion and actual:
            return actual

        if opcion in opciones:
            return opciones[opcion]

        print(notificacion_error("Opción inválida."))


def pedir_protocolo(
    actual: str = ""
) -> str:
    opciones = {
        "1": "OpenVPN",
        "2": "FortiClient",
        "3": "GlobalProtect",
        "4": "Cisco AnyConnect"
    }

    while True:
        print()
        if actual:
            print(campo("Protocolo actual", actual))
            print()

        print(opcion_menu("1", "OpenVPN"))
        print(opcion_menu("2", "FortiClient"))
        print(opcion_menu("3", "GlobalProtect"))
        print(opcion_menu("4", "Cisco AnyConnect"))
        print()

        opcion = input_con_control(prompt("Seleccione protocolo"))

        if not opcion and actual in opciones.values():
            return actual

        if opcion in opciones:
            return opciones[opcion]

        print(notificacion_error("Opción inválida."))


def pedir_puerto_server(
    actual: str = "8888"
) -> str:
    if not actual:
        actual = "8888"

    while True:
        lbl = f"Puerto Server {Color.DIM}[{actual}]{Color.RESET}"
        puerto = input_con_control(prompt(lbl)).strip()

        if not puerto:
            return actual

        if puerto.isdigit() and len(puerto) == 4:
            return puerto

        print(notificacion_error("El puerto debe ser un número de 4 dígitos (ej. 8888, 7777, 8989)."))


def pedir_con_default_obligatorio(
    mensaje: str,
    actual: str = ""
) -> str:
    return actual


def pedir_opcion_si_no(
    texto: str,
    actual: str = ""
):
    while True:
        lbl = f"{texto} {Color.DIM}[{actual}]{Color.RESET} (S/N)" if actual else f"{texto} (S/N)"
        valor = input_con_control(prompt(lbl)).upper()

        if not valor and actual:
            return actual

        if valor == "S":
            return "Si"

        if valor == "N":
            return "No"

        print(notificacion_error("Ingrese S o N."))


def formatear_elemento(
    self,
    elemento: dict
):
    if elemento["tipo"] == "Otro":
        return elemento["descripcion"]

    if elemento.get("metraje"):
        return f"{elemento['tipo']} {elemento['metraje']}m"

    return elemento["tipo"]


def pedir_encargado_area(
    valor_actual=""
):
    encargados = list(ENCARGADOS.keys())

    while True:
        print()
        if valor_actual:
            print(campo("Encargado actual", valor_actual))
            print()

        for i, encargado in enumerate(encargados, start=1):
            print(opcion_menu(str(i), encargado))

        print(opcion_menu(str(len(encargados) + 1), "Otro"))
        print()

        opcion = input_con_control(prompt("Seleccione encargado"))

        if not opcion and valor_actual:
            return valor_actual

        if not opcion.isdigit():
            print(notificacion_error("Opción inválida"))
            continue

        opc_num = int(opcion)

        if 1 <= opc_num <= len(encargados):
            return encargados[opc_num - 1]

        if opc_num == (len(encargados) + 1):
            return input_con_control(prompt("Nombre encargado"))

        print(notificacion_error("Opción inválida"))


def pedir_tecnico_visita(
    encargado,
    valor_actual=""
):
    if encargado in ENCARGADOS:
        tecnicos = ENCARGADOS[encargado]
    else:
        tecnicos = []
        for lista in ENCARGADOS.values():
            tecnicos.extend(lista)
        tecnicos = sorted(list(set(tecnicos)))

    while True:
        print()
        if valor_actual:
            print(campo("Técnico actual", valor_actual))
            print()

        for i, tecnico in enumerate(tecnicos, start=1):
            print(opcion_menu(str(i), tecnico))

        print(opcion_menu(str(len(tecnicos) + 1), "Otro"))
        print()

        opcion = input_con_control(prompt("Seleccione técnico"))

        if not opcion and valor_actual:
            return valor_actual

        if not opcion.isdigit():
            print(notificacion_error("Opción inválida"))
            continue

        opc_num = int(opcion)

        if 1 <= opc_num <= len(tecnicos):
            return tecnicos[opc_num - 1]

        if opc_num == (len(tecnicos) + 1):
            return input_con_control(prompt("Nombre técnico"))

        print(notificacion_error("Opción inválida"))


def pedir_empresa(
    valor_actual=""
):
    while True:
        print()
        if valor_actual:
            print(campo("Empresa actual", valor_actual))
            print()

        for i, empresa in enumerate(EMPRESAS, start=1):
            print(opcion_menu(str(i), empresa))

        print(opcion_menu(str(len(EMPRESAS) + 1), "Otro"))
        print()

        opcion = input_con_control(prompt("Seleccione empresa"))

        if not opcion and valor_actual:
            return valor_actual

        if not opcion.isdigit():
            print(notificacion_error("Opción inválida"))
            continue

        opc_num = int(opcion)

        if 1 <= opc_num <= len(EMPRESAS):
            return EMPRESAS[opc_num - 1]

        if opc_num == (len(EMPRESAS) + 1):
            nombre = input_con_control(prompt("Nombre empresa"))
            if nombre:
                return nombre

        print(notificacion_error("Opción inválida"))