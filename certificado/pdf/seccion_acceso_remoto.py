from .plantilla import MARGEN_X, dibujar_titulo_seccion, dibujar_tabla_atributo_valor


def agregar_acceso_remoto(pdf, datos, y):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "3. ACCESO REMOTO")

    host_server = datos.get("hostserver") or datos.get("host_server") or "dataweb.innovex.cl"
    puerto_server = datos.get("puerto_server") or "8888"

    filas = [
        ("Protocolo", datos.get("protocolo", "")),
        ("Tun0", datos.get("tun0", "")),
        ("IP Fija", datos.get("ip_fija", "")),
        ("Host Server", host_server),
        ("Puerto Server", puerto_server)
    ]

    y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas, col_ratio=0.35, alto_fila=18)
    return y

