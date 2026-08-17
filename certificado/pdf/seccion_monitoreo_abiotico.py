from .plantilla import MARGEN_X, dibujar_titulo_seccion, dibujar_tabla_atributo_valor


def agregar_monitoreo_abiotico(pdf, datos, y):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "5. MONITOREO ABIÓTICO")

    instalado = datos.get("instalado", "No")

    if instalado == "Si":
        filas = [
            ("Instalado", instalado),
            ("Versión", datos.get("version", "")),
            ("Dirección MAC", datos.get("mac", "")),
            ("PanID", datos.get("panid", ""))
        ]
    else:
        filas = [
            ("Instalado", "No")
        ]

    y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas, col_ratio=0.35, alto_fila=18)
    return y

