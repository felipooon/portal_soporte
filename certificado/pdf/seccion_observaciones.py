from .plantilla import (
    MARGEN_X, ANCHO_UTIL, COLOR_TEXTO_TABLA, COLOR_BORDE_TABLA, COLOR_HEADER_BG,
    dibujar_titulo_seccion
)


def agregar_observaciones(pdf, observaciones, y):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "8. Observaciones y notas")

    texto = observaciones.strip() if isinstance(observaciones, str) and observaciones.strip() else ""

    if texto:
        max_ancho = ANCHO_UTIL - 16
        palabras = texto.split(" ")
        lineas = []
        linea_actual = ""

        for palabra in palabras:
            probando = f"{linea_actual} {palabra}".strip()
            if pdf.stringWidth(probando, "Helvetica", 8.5) <= max_ancho:
                linea_actual = probando
            else:
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        alto_caja = max(len(lineas) * 14 + 10, 50)
    else:
        lineas = []
        alto_caja = 60  # Espacio libre para llenado manual por el cliente / técnico

    # Dibujar caja con estilo de la plantilla oficial
    pdf.setFillColor(COLOR_HEADER_BG)
    pdf.setStrokeColor(COLOR_BORDE_TABLA)
    pdf.setLineWidth(0.5)
    pdf.rect(MARGEN_X, y - alto_caja, ANCHO_UTIL, alto_caja, fill=True, stroke=True)

    if lineas:
        y_pos = y - 14
        pdf.setFont("Helvetica", 8.5)
        pdf.setFillColor(COLOR_TEXTO_TABLA)

        for lin in lineas:
            pdf.drawString(MARGEN_X + 8, y_pos, lin)
            y_pos -= 14

    return y - alto_caja - 14
