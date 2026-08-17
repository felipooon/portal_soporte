from .plantilla import MARGEN_X, dibujar_titulo_seccion, dibujar_tabla_atributo_valor


def agregar_datos_generales(pdf, datos, y):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "1. Información general del centro")

    encargado = datos.get("encargado_area") or datos.get("encargado_centro") or datos.get("encargado") or "-"
    telefono = datos.get("telefono_centro") or datos.get("numero_centro") or datos.get("telefono") or "-"

    filas = [
        ("Empresa", datos.get("empresa", "-")),
        ("Centro", datos.get("nombre_centro", "-")),
        ("Encargado de área", encargado),
        ("Ficha", datos.get("numero_ficha", "-")),
        ("Fecha", datos.get("fecha_instalacion", "-")),
        ("Técnico responsable", datos.get("tecnico_visita", "-")),
        ("Teléfono del centro", telefono),
        ("Correo del centro", datos.get("correo_centro", "-")),
        ("Coordenadas", datos.get("coordenadas", "-")),
        ("Barrio", datos.get("barrio", "-")),
        ("Puerto patrón", datos.get("puerto_patron", "-"))
    ]

    y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas, col_ratio=0.35, alto_fila=18)
    return y