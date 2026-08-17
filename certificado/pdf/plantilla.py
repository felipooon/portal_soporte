import sys
from pathlib import Path
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

if hasattr(sys, "_MEIPASS"):
    BASE_DIR = Path(getattr(sys, "_MEIPASS"))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

ASSETS_DIR = BASE_DIR / "assets"

MEMBRETE = ASSETS_DIR / "membrete_soporte.png"
LOGO_INNOVEX = ASSETS_DIR / "logo_innovex.png"

MARGEN_X = 40
MARGEN_Y = 40

ANCHO_PAGINA = 595.27
ALTO_PAGINA = 841.89
ANCHO_UTIL = ANCHO_PAGINA - (2 * MARGEN_X)  # 515.27 pt

TITULO = "VALIDACIÓN DE INSTALACIÓN"

# Paleta de Colores Ficha Oficial Innovex
COLOR_NEGRO = colors.HexColor("#000000")
COLOR_HEADER_BG = colors.HexColor("#f2f2f2")
COLOR_BORDE_TABLA = colors.HexColor("#cccccc")
COLOR_TEXTO_TABLA = colors.HexColor("#111111")
COLOR_SUBTITULO = colors.HexColor("#333333")


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para calcular dinámicamente el total de páginas 'X de Y'
    y renderizar el encabezado oficial de Innovex en cada página."""

    def __init__(self, *args, codigo_registro="DS-001", **kwargs):
        super().__init__(*args, **kwargs)
        self.codigo_registro = codigo_registro
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()  # pyrefly: ignore [missing-attribute]

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()

        # Posición del encabezado superior oficial
        y_top = ALTO_PAGINA - 35
        alto_header = 46
        x = MARGEN_X
        ancho = ANCHO_UTIL

        w_left = 160.0
        w_right = 120.0
        w_center = ancho - w_left - w_right

        # Borde exterior del encabezado
        self.setStrokeColor(COLOR_BORDE_TABLA)
        self.setLineWidth(0.8)
        self.rect(x, y_top - alto_header, ancho, alto_header, fill=False, stroke=True)

        # 1. Bloque Izquierdo: Logo / Marca Innovex
        self.setFillColor(COLOR_NEGRO)
        self.rect(x, y_top - alto_header, w_left, alto_header, fill=True, stroke=True)

        logo_path = LOGO_INNOVEX if LOGO_INNOVEX.exists() else MEMBRETE
        if logo_path.exists():
            try:
                self.drawImage(
                    str(logo_path),
                    x + 4,
                    y_top - alto_header + 3,
                    width=w_left - 8,
                    height=alto_header - 6,
                    preserveAspectRatio=True,
                    anchor='c',
                    mask='auto'
                )
            except Exception:
                self.setFillColor(colors.white)
                self.setFont("Helvetica-Bold", 16)
                self.drawString(x + 10, y_top - 25, "innovex")
                self.setFont("Helvetica", 7)
                self.drawString(x + 10, y_top - 36, "SOLUCIONES TECNOLÓGICAS")
        else:
            self.setFillColor(colors.white)
            self.setFont("Helvetica-Bold", 16)
            self.drawString(x + 10, y_top - 25, "innovex")
            self.setFont("Helvetica", 7)
            self.drawString(x + 10, y_top - 36, "SOLUCIONES TECNOLÓGICAS")

        # 2. Bloque Central: Título Documento
        x_center = x + w_left
        self.setStrokeColor(COLOR_BORDE_TABLA)
        self.line(x_center, y_top - alto_header, x_center, y_top)

        self.setFillColor(COLOR_NEGRO)
        self.setFont("Helvetica-Bold", 10.5)
        self.drawCentredString(x_center + (w_center / 2.0), y_top - (alto_header / 2.0) - 3, "VALIDACIÓN DE INSTALACIÓN")

        # 3. Bloque Derecho: Control Ficha
        x_right = x_center + w_center
        self.line(x_right, y_top - alto_header, x_right, y_top)

        row_h = alto_header / 3.0
        c_val_x = x_right + 50.0

        page_num = getattr(self, "_pageNumber", 1)  # pyrefly: ignore [missing-attribute]
        labels = [
            ("Registro", self.codigo_registro),
            ("Periodo", "2026"),
            ("Páginas", f"{page_num} de {page_count}")
        ]

        for i, (lbl, val) in enumerate(labels):
            ry = y_top - ((i + 1) * row_h)
            if i < 2:
                self.line(x_right, ry, x_right + w_right, ry)

            self.line(c_val_x, ry, c_val_x, ry + row_h)

            self.setFillColor(COLOR_NEGRO)
            self.setFont("Helvetica", 8)
            self.drawString(x_right + 5, ry + 4, lbl)
            self.drawCentredString(c_val_x + ((w_right - 50.0) / 2.0), ry + 4, val)

        self.restoreState()


def dibujar_titulo_seccion(pdf, x, y, titulo):
    """Dibuja el título numerado de la sección (ej. '1. Información general del centro')."""
    pdf.setFillColor(COLOR_NEGRO)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(x, y - 14, titulo)
    return y - 22


def dibujar_subtitulo(pdf, x, y, subtitulo):
    """Dibuja un subtítulo secundario de la sección."""
    pdf.setFillColor(COLOR_SUBTITULO)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x, y - 12, subtitulo)
    return y - 18


def dibujar_tabla_atributo_valor(pdf, x, y, filas_datos, col_ratio=0.35, alto_fila=18):
    """
    Dibuja una tabla oficial atributo-valor (2 columnas) que ocupa todo el ancho útil.
    filas_datos: lista de tuplas (atributo, valor)
    """
    if not filas_datos:
        return y

    pdf.saveState()
    ancho = ANCHO_UTIL
    w_attr = ancho * col_ratio
    w_val = ancho - w_attr

    for attr, val in filas_datos:
        y_top_row = y

        # Fondo gris columna atributo
        pdf.setFillColor(COLOR_HEADER_BG)
        pdf.setStrokeColor(COLOR_BORDE_TABLA)
        pdf.setLineWidth(0.5)
        pdf.rect(x, y_top_row - alto_fila, w_attr, alto_fila, fill=True, stroke=True)

        # Fondo blanco columna valor
        pdf.setFillColor(colors.white)
        pdf.rect(x + w_attr, y_top_row - alto_fila, w_val, alto_fila, fill=True, stroke=True)

        # Texto Atributo
        pdf.setFillColor(COLOR_NEGRO)
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawString(x + 8, y_top_row - alto_fila + 5, str(attr))

        # Texto Valor
        pdf.setFont("Helvetica", 8.5)
        pdf.setFillColor(COLOR_TEXTO_TABLA)
        pdf.drawString(x + w_attr + 8, y_top_row - alto_fila + 5, str(val if val is not None else ""))

        y -= alto_fila

    pdf.restoreState()
    return y - 10


def dibujar_cabecera_tabla(pdf, x, y, cabeceras, anchos_cols, alto_fila):
    pdf.setFillColor(COLOR_NEGRO)
    pdf.setStrokeColor(COLOR_BORDE_TABLA)
    pdf.setLineWidth(0.5)
    pdf.rect(x, y - alto_fila, ANCHO_UTIL, alto_fila, fill=True, stroke=True)

    curr_x = x
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 7.5)

    for i, h_text in enumerate(cabeceras):
        w_c = anchos_cols[i]
        pdf.drawCentredString(curr_x + (w_c / 2.0), y - alto_fila + 5, str(h_text))
        curr_x += w_c

    return y - alto_fila


def dibujar_tabla_listado(pdf, x, y, cabeceras, filas_datos, anchos_relativos=None, alto_fila=18):
    """
    Dibuja una tabla con cabecera en negro/texto blanco y filas de datos tabulares.
    Soporta saltos de página automáticos cuando los datos exceden la página actual.
    """
    if not cabeceras:
        return y

    ancho = ANCHO_UTIL
    num_cols = len(cabeceras)

    if not anchos_relativos or len(anchos_relativos) != num_cols:
        anchos_cols = [ancho / num_cols] * num_cols
    else:
        tot = float(sum(anchos_relativos))
        anchos_cols = [(w / tot) * ancho for w in anchos_relativos]

    # Verificar si cabe la cabecera + al menos 1 fila
    if y - (alto_fila * 2) < 45:
        pdf.showPage()
        y = ALTO_PAGINA - 90

    # Dibujar cabecera
    y = dibujar_cabecera_tabla(pdf, x, y, cabeceras, anchos_cols, alto_fila)

    # Filas de Datos
    pdf.setFont("Helvetica", 7)
    for row_idx, fila in enumerate(filas_datos):
        if y - alto_fila < 45:
            pdf.showPage()
            y = ALTO_PAGINA - 90
            y = dibujar_cabecera_tabla(pdf, x, y, cabeceras, anchos_cols, alto_fila)
            pdf.setFont("Helvetica", 7)

        y_top_r = y
        bg_col = colors.white if row_idx % 2 == 0 else colors.HexColor("#fcfcfc")

        curr_x = x
        for i, val in enumerate(fila):
            w_c = anchos_cols[i]
            pdf.setFillColor(bg_col)
            pdf.rect(curr_x, y_top_r - alto_fila, w_c, alto_fila, fill=True, stroke=True)

            val_str = str(val if val is not None else "")
            # Ajustar texto largo para evitar desbordamientos laterales
            max_chars = max(4, int(w_c / 4.8))
            if len(val_str) > max_chars:
                val_str = val_str[:max_chars - 2] + ".."

            pdf.setFillColor(COLOR_TEXTO_TABLA)
            pdf.drawCentredString(curr_x + (w_c / 2.0), y_top_r - alto_fila + 5, val_str)
            curr_x += w_c

        y -= alto_fila

    return y - 10