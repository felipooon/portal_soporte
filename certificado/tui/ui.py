"""
Motor visual centralizado para la TUI.
Provee colores ANSI, cajas Unicode, barras de progreso,
badges de estado, breadcrumbs y utilidades de presentación.
Compatible con cualquier terminal moderna sin dependencias externas.
"""
import os
import sys
import shutil
import subprocess


# ─── Detección de soporte de color ────────────────────────────────────────────

def _soporta_color() -> bool:
    """Detecta si la terminal soporta colores ANSI."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    term = os.environ.get("TERM", "")
    if term == "dumb":
        return False
    return True


SOPORTA_COLOR = _soporta_color()


# ─── Colores ANSI ────────────────────────────────────────────────────────────

class Color:
    """Constantes de color ANSI con fallback a texto plano."""

    if SOPORTA_COLOR:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        DIM = "\033[2m"
        ITALIC = "\033[3m"
        UNDERLINE = "\033[4m"

        # Colores base
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"

        # Colores brillantes
        BRIGHT_BLACK = "\033[90m"
        BRIGHT_RED = "\033[91m"
        BRIGHT_GREEN = "\033[92m"
        BRIGHT_YELLOW = "\033[93m"
        BRIGHT_BLUE = "\033[94m"
        BRIGHT_MAGENTA = "\033[95m"
        BRIGHT_CYAN = "\033[96m"
        BRIGHT_WHITE = "\033[97m"

        # Fondos
        BG_CYAN = "\033[46m"
        BG_GREEN = "\033[42m"
        BG_YELLOW = "\033[43m"
        BG_RED = "\033[41m"
        BG_BLUE = "\033[44m"
        BG_MAGENTA = "\033[45m"
    else:
        RESET = BOLD = DIM = ITALIC = UNDERLINE = ""
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        BRIGHT_BLACK = BRIGHT_RED = BRIGHT_GREEN = BRIGHT_YELLOW = ""
        BRIGHT_BLUE = BRIGHT_MAGENTA = BRIGHT_CYAN = BRIGHT_WHITE = ""
        BG_CYAN = BG_GREEN = BG_YELLOW = BG_RED = BG_BLUE = BG_MAGENTA = ""


# ─── Símbolos Unicode ─────────────────────────────────────────────────────────

class Icono:
    """Símbolos Unicode simples para la interfaz."""
    CHECK = "✔"
    CROSS = "✘"
    BULLET = "●"
    HALF = "◐"
    ARROW = "▸"
    DOT = "·"


# ─── Utilidades base ─────────────────────────────────────────────────────────

def ancho_terminal() -> int:
    """Retorna el ancho de la terminal, con un mínimo de 50."""
    try:
        return max(50, shutil.get_terminal_size().columns)
    except Exception:
        return 80


def limpiar_pantalla():
    """Limpia la terminal."""
    if sys.stdout.isatty():
        subprocess.run("clear" if os.name != "nt" else "cls", shell=True)


def _len_visible(texto: str) -> int:
    """Calcula la longitud visible de un texto, ignorando secuencias ANSI."""
    import re
    return len(re.sub(r'\033\[[0-9;]*m', '', texto))


def _truncar_o_ajustar(texto: str, max_visible: int) -> str:
    """Asegura que el texto visible no sobrepase max_visible caracteres."""
    if _len_visible(texto) <= max_visible:
        return texto
    import re
    texto_limpio = re.sub(r'\033\[[0-9;]*m', '', texto)
    if len(texto_limpio) > max_visible:
        limite = max(0, max_visible - 3)
        return texto_limpio[:limite] + "..."
    return texto_limpio


# ─── Cajas y Encabezados ─────────────────────────────────────────────────────

def caja(titulo: str, subtitulo: str = "", ancho: int = 0, color: str = "") -> str:
    """
    Dibuja un encabezado con bordes Unicode alineados perfectamente.
    """
    if not color:
        color = Color.CYAN

    tit_visible = _len_visible(titulo)
    sub_visible = _len_visible(subtitulo) if subtitulo else 0
    max_text_len = max(tit_visible, sub_visible)

    ancho_max = max(50, ancho_terminal() - 4)
    if not ancho:
        ancho = min(ancho_max, max(56, max_text_len + 4))

    interior = ancho - 2  # espacio entre ║ y ║
    max_visible = interior - 2  # espacio libre para texto tras los 2 espacios de margen

    lineas = []
    lineas.append(f"{color}╔{'═' * interior}╗{Color.RESET}")

    # Título
    tit_adj = _truncar_o_ajustar(titulo, max_visible)
    pad_titulo = max(0, max_visible - _len_visible(tit_adj))
    lineas.append(f"{color}║{Color.RESET}  {tit_adj}{' ' * pad_titulo}{color}║{Color.RESET}")

    # Subtítulo
    if subtitulo:
        sub_adj = _truncar_o_ajustar(subtitulo, max_visible)
        pad_sub = max(0, max_visible - _len_visible(sub_adj))
        lineas.append(f"{color}║{Color.RESET}  {sub_adj}{' ' * pad_sub}{color}║{Color.RESET}")

    lineas.append(f"{color}╚{'═' * interior}╝{Color.RESET}")

    return "\n".join(lineas)


def caja_doble(titulo: str, subtitulo: str = "", info_extra: str = "", ancho: int = 0) -> str:
    """
    Caja con línea extra de información (ej. barra de progreso).
    """
    color = Color.CYAN
    tit_v = _len_visible(titulo)
    sub_v = _len_visible(subtitulo) if subtitulo else 0
    inf_v = _len_visible(info_extra) if info_extra else 0
    max_text_len = max(tit_v, sub_v, inf_v)

    ancho_max = max(50, ancho_terminal() - 4)
    if not ancho:
        ancho = min(ancho_max, max(56, max_text_len + 4))

    interior = ancho - 2
    max_visible = interior - 2

    lineas = []
    lineas.append(f"{color}╔{'═' * interior}╗{Color.RESET}")

    # Título
    tit_adj = _truncar_o_ajustar(titulo, max_visible)
    pad = max(0, max_visible - _len_visible(tit_adj))
    lineas.append(f"{color}║{Color.RESET}  {tit_adj}{' ' * pad}{color}║{Color.RESET}")

    # Subtítulo
    if subtitulo:
        sub_adj = _truncar_o_ajustar(subtitulo, max_visible)
        pad_sub = max(0, max_visible - _len_visible(sub_adj))
        lineas.append(f"{color}║{Color.RESET}  {sub_adj}{' ' * pad_sub}{color}║{Color.RESET}")

    # Info extra
    if info_extra:
        inf_adj = _truncar_o_ajustar(info_extra, max_visible)
        pad_info = max(0, max_visible - _len_visible(inf_adj))
        lineas.append(f"{color}║{Color.RESET}  {inf_adj}{' ' * pad_info}{color}║{Color.RESET}")

    lineas.append(f"{color}╚{'═' * interior}╝{Color.RESET}")
    return "\n".join(lineas)


# ─── Barras de Progreso ──────────────────────────────────────────────────────

def barra_progreso(completados: int, total: int, ancho: int = 20) -> str:
    """
    Genera una barra de progreso visual.

    [████████████░░░░░░░░] 60%
    """
    if total <= 0:
        total = 1
    ratio = min(completados / total, 1.0)
    llenos = int(ratio * ancho)
    vacios = ancho - llenos

    if ratio >= 1.0:
        color = Color.BRIGHT_GREEN
    elif ratio >= 0.5:
        color = Color.BRIGHT_YELLOW
    elif ratio > 0:
        color = Color.YELLOW
    else:
        color = Color.BRIGHT_BLACK

    porcentaje = int(ratio * 100)
    barra = f"{color}{'█' * llenos}{'░' * vacios}{Color.RESET}"
    return f"[{barra}] {porcentaje}%"


def barra_progreso_mini(completados: int, total: int, ancho: int = 15) -> str:
    """Barra de progreso compacta sin porcentaje."""
    if total <= 0:
        total = 1
    ratio = min(completados / total, 1.0)
    llenos = int(ratio * ancho)
    vacios = ancho - llenos

    if ratio >= 1.0:
        color = Color.BRIGHT_GREEN
    elif ratio > 0:
        color = Color.YELLOW
    else:
        color = Color.BRIGHT_BLACK

    return f"{color}{'█' * llenos}{'░' * vacios}{Color.RESET}"


# ─── Badges de Estado ────────────────────────────────────────────────────────

def badge_estado(completados: int, total: int) -> str:
    """
    Retorna un badge de estado coloreado.
    ✔ Completo | ◐ Parcial | ✘ Vacío
    """
    if total <= 0:
        total = 1
    ratio = completados / total

    if ratio >= 1.0:
        return f"{Color.BRIGHT_GREEN}{Icono.CHECK}{Color.RESET}"
    elif ratio > 0:
        return f"{Color.YELLOW}{Icono.HALF}{Color.RESET}"
    else:
        return f"{Color.BRIGHT_BLACK}{Icono.CROSS}{Color.RESET}"


def badge_bool(valor: bool) -> str:
    """Badge para valores booleanos Sí/No."""
    if valor:
        return f"{Color.BRIGHT_GREEN}Si{Color.RESET}"
    else:
        return f"{Color.BRIGHT_RED}No{Color.RESET}"


# ─── Campos y Tablas ─────────────────────────────────────────────────────────

def campo(label: str, valor: str, ancho_label: int = 22) -> str:
    """
    Muestra un campo con color según si tiene valor o está vacío.
    Label alineado + valor coloreado.
    """
    label_fmt = f"{Color.DIM}{label + ':':<{ancho_label}}{Color.RESET}"
    if valor:
        valor_fmt = f"{Color.BRIGHT_WHITE}{valor}{Color.RESET}"
    else:
        valor_fmt = f"{Color.BRIGHT_BLACK}—{Color.RESET}"
    return f"  {label_fmt} {valor_fmt}"


def campo_bool(label: str, valor: bool, ancho_label: int = 22) -> str:
    """Campo para valores booleanos."""
    label_fmt = f"{Color.DIM}{label + ':':<{ancho_label}}{Color.RESET}"
    valor_fmt = badge_bool(valor)
    return f"  {label_fmt} {valor_fmt}"


# ─── Opciones de Menú ────────────────────────────────────────────────────────

def opcion_menu(tecla: str, texto: str, icono: str = "") -> str:
    """Formatea una opción de menú con estilo."""
    icono_str = f"{icono} " if icono else ""
    return (
        f"  {Color.CYAN}{Color.BOLD}[{tecla}]{Color.RESET}"
        f"  {icono_str}{texto}"
    )


def opcion_seccion(num: int, titulo: str, completados: int, total: int) -> str:
    """
    Opción de menú para una sección del certificado con badge + barra.

    ✔ 1. Datos Generales          [███████████████████] 7/7
    """
    badge = badge_estado(completados, total)
    barra = barra_progreso_mini(completados, total, ancho=15)
    conteo = f"{Color.DIM}{completados}/{total}{Color.RESET}"

    titulo_fmt = f"{titulo:<26}"
    return f"  {badge} {Color.BOLD}{num}.{Color.RESET} {titulo_fmt} {barra} {conteo}"


# ─── Separadores y Navegación ────────────────────────────────────────────────

def separador(ancho: int = 0) -> str:
    """Línea divisoria elegante."""
    if not ancho:
        ancho = min(54, ancho_terminal() - 6)
    return f"  {Color.BRIGHT_BLACK}{'─' * ancho}{Color.RESET}"


def breadcrumb(*partes: str) -> str:
    """
    Muestra la ruta de navegación.
    Inicio ▸ Certificado ▸ Datos Generales
    """
    flecha = f" {Color.BRIGHT_BLACK}{Icono.ARROW}{Color.RESET} "
    partes_fmt = []
    for i, parte in enumerate(partes):
        if i == len(partes) - 1:
            # Última parte en blanco brillante
            partes_fmt.append(f"{Color.BRIGHT_WHITE}{parte}{Color.RESET}")
        else:
            partes_fmt.append(f"{Color.BRIGHT_BLACK}{parte}{Color.RESET}")
    return f"  {flecha.join(partes_fmt)}"


# ─── Notificaciones ──────────────────────────────────────────────────────────

def notificacion_exito(mensaje: str) -> str:
    """Mensaje de éxito estilizado."""
    return f"\n  {Color.BRIGHT_GREEN}{Icono.CHECK} {mensaje}{Color.RESET}"


def notificacion_error(mensaje: str) -> str:
    """Mensaje de error estilizado."""
    return f"\n  {Color.BRIGHT_RED}{Icono.CROSS} {mensaje}{Color.RESET}"


def notificacion_advertencia(mensaje: str) -> str:
    """Mensaje de advertencia estilizado."""
    return f"\n  {Color.YELLOW}{Icono.BULLET} {mensaje}{Color.RESET}"


def notificacion_info(mensaje: str) -> str:
    """Mensaje informativo estilizado."""
    return f"\n  {Color.BRIGHT_CYAN}{Icono.BULLET} {mensaje}{Color.RESET}"


# ─── Barra de Acciones ───────────────────────────────────────────────────────

def barra_acciones(*acciones: tuple) -> str:
    """
    Barra compacta de acciones en una línea.
    Recibe tuplas (tecla, texto).

    [A] Auto-rellenar   [G] Guardar   [P] PDF   [V] Volver
    """
    partes = []
    for tecla, texto in acciones:
        partes.append(
            f"{Color.CYAN}[{tecla}]{Color.RESET} {texto}"
        )
    return "  " + "   ".join(partes)


# ─── Progreso Global ─────────────────────────────────────────────────────────

def progreso_global(secciones_completadas: int, total_secciones: int) -> str:
    """
    Línea de progreso global para el encabezado del certificado.
    Progreso: [████████████████░░░░] 80%  (7/9)
    """
    barra = barra_progreso(secciones_completadas, total_secciones, ancho=20)
    return f"{Color.DIM}Progreso:{Color.RESET} {barra}  ({secciones_completadas}/{total_secciones})"


# ─── Prompt estilizado ───────────────────────────────────────────────────────

def prompt(texto: str = "Seleccione una opción") -> str:
    """Input prompt estilizado."""
    return f"\n  {Color.BRIGHT_CYAN}{Icono.ARROW}{Color.RESET} {texto}: "


# ─── Tabla de datos ──────────────────────────────────────────────────────────

def encabezado_tabla(*columnas: tuple) -> str:
    """
    Encabezado de tabla formateado.
    Recibe tuplas (nombre, ancho).
    """
    partes = []
    for nombre, ancho in columnas:
        partes.append(f"{Color.BOLD}{nombre:<{ancho}}{Color.RESET}")
    header = f"  {' │ '.join(partes)}"
    # Línea separadora
    anchos = [a for _, a in columnas]
    linea = f"  {'─┼─'.join('─' * a for a in anchos)}"
    return f"{header}\n{Color.BRIGHT_BLACK}{linea}{Color.RESET}"


def fila_tabla(*valores: tuple) -> str:
    """
    Fila de tabla formateada.
    Recibe tuplas (valor, ancho).
    """
    partes = []
    for valor, ancho in valores:
        texto = str(valor)[:ancho]
        partes.append(f"{texto:<{ancho}}")
    return f"  {f' │ '.join(partes)}"


# ─── Banner de bienvenida ────────────────────────────────────────────────────

def banner_bienvenida() -> str:
    """Banner ASCII de la aplicación."""
    color = Color.CYAN
    bold = Color.BOLD
    reset = Color.RESET

    return f"""
{color}{bold}    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║              {reset}{bold}CERTIFICADO DE INSTALACIÓN{reset}{color}{bold}               ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝{reset}
"""


# ─── Sección de edición ──────────────────────────────────────────────────────

def encabezado_edicion(titulo: str) -> str:
    """Encabezado estilizado para modo de edición."""
    tit_v = _len_visible(titulo)
    tip_str = "Tip: ':c' cancelar │ ':g' guardar avance"
    tip_v = _len_visible(tip_str)
    max_text_len = max(tit_v, tip_v)

    ancho_max = max(50, ancho_terminal() - 4)
    ancho = min(ancho_max, max(56, max_text_len + 4))
    interior = ancho - 2
    max_visible = interior - 2

    color = Color.YELLOW
    lineas = []
    lineas.append(f"{color}┌{'─' * interior}┐{Color.RESET}")

    titulo_fmt = f"{Color.BOLD}{titulo}{Color.RESET}"
    tit_adj = _truncar_o_ajustar(titulo_fmt, max_visible)
    pad = max(0, max_visible - _len_visible(tit_adj))
    lineas.append(f"{color}│{Color.RESET}  {tit_adj}{' ' * pad}{color}│{Color.RESET}")

    tip1 = f"{Color.DIM}{tip_str}{Color.RESET}"
    tip_adj = _truncar_o_ajustar(tip1, max_visible)
    pad_tip = max(0, max_visible - _len_visible(tip_adj))
    lineas.append(f"{color}│{Color.RESET}  {tip_adj}{' ' * pad_tip}{color}│{Color.RESET}")

    lineas.append(f"{color}└{'─' * interior}┘{Color.RESET}")
    return "\n".join(lineas)


def encabezado_pegar(titulo: str, instrucciones: list[str] | None = None) -> str:
    """Encabezado para secciones de pegar texto de consola."""
    max_text_len = _len_visible(titulo)
    if instrucciones:
        for instr in instrucciones:
            max_text_len = max(max_text_len, _len_visible(instr))

    ancho_max = max(50, ancho_terminal() - 4)
    ancho = min(ancho_max, max(62, max_text_len + 4))
    interior = ancho - 2
    max_visible = interior - 2

    color = Color.MAGENTA
    lineas = []
    lineas.append(f"{color}┌{'─' * interior}┐{Color.RESET}")

    titulo_fmt = f"{Color.BOLD}{titulo}{Color.RESET}"
    tit_adj = _truncar_o_ajustar(titulo_fmt, max_visible)
    pad = max(0, max_visible - _len_visible(tit_adj))
    lineas.append(f"{color}│{Color.RESET}  {tit_adj}{' ' * pad}{color}│{Color.RESET}")

    if instrucciones:
        for instr in instrucciones:
            instr_fmt = f"{Color.DIM}{instr}{Color.RESET}"
            instr_adj = _truncar_o_ajustar(instr_fmt, max_visible)
            pad_i = max(0, max_visible - _len_visible(instr_adj))
            lineas.append(f"{color}│{Color.RESET}  {instr_adj}{' ' * pad_i}{color}│{Color.RESET}")

    lineas.append(f"{color}└{'─' * interior}┘{Color.RESET}")
    return "\n".join(lineas)


# ─── Lista de items con icono ─────────────────────────────────────────────────

def item_lista(idx: int, texto: str, detalle: str = "") -> str:
    """Ítem de lista numerado con formato."""
    num = f"{Color.CYAN}{Color.BOLD}{idx}.{Color.RESET}"
    if detalle:
        return f"  {num} {texto} {Color.DIM}{detalle}{Color.RESET}"
    return f"  {num} {texto}"


def item_archivo(nombre: str, estado: str = "+") -> str:
    """Ítem de archivo con ícono de estado."""
    if estado == "+":
        icono = f"{Color.BRIGHT_GREEN}[+]{Color.RESET}"
    elif estado == "-":
        icono = f"{Color.BRIGHT_RED}[-]{Color.RESET}"
    else:
        icono = f"{Color.BRIGHT_BLACK}[·]{Color.RESET}"
    return f"    {icono} {nombre}"


def texto_vacio(mensaje: str) -> str:
    """Texto para cuando no hay items."""
    return f"  {Color.BRIGHT_BLACK}{Icono.DOT} {mensaje}{Color.RESET}"
