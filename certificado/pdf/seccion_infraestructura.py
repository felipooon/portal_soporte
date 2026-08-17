from .plantilla import MARGEN_X, dibujar_titulo_seccion, dibujar_tabla_atributo_valor


def agregar_infraestructura(pdf, datos, y, certificado=None):
    if certificado is None:
        certificado = {}

    acceso = certificado.get("acceso_remoto", {})
    act = certificado.get("activacion", {})

    tipo_ip = datos.get("tipo_ip") or "IP VPN tun0"
    ip_fija = datos.get("ip_fija") or acceso.get("ip_fija") or act.get("ip_final") or "-"
    ip_vpn = datos.get("ip_vpn") or acceso.get("tun0") or act.get("vpn_tun0") or "-"

    filas = [
        ("Área", datos.get("area", "-")),
        ("Tipo PC", datos.get("categoria", "Notebook")),
        ("Marca / Modelo", f"{datos.get('marca', '')} {datos.get('modelo', '')}".strip() or "-"),
        ("Sistema Operativo", datos.get("sistema_operativo") or datos.get("so") or "-"),
        ("Kernel", datos.get("kernel", "-")),
        ("MAC Ethernet", datos.get("mac_ethernet", "-")),
        ("MAC Wi-Fi", datos.get("mac_wifi", "-")),
        ("ID Equipo / PC", datos.get("pc_id", "-")),
        ("Contraseña PC", datos.get("pc_password", "-")),
        ("Tipo de Conexión IP", tipo_ip)
    ]

    if tipo_ip in ("IP Fija", "Ambas"):
        filas.append(("IP Fija PC", ip_fija))
    if tipo_ip in ("IP VPN tun0", "Ambas"):
        filas.append(("IP VPN tun0", ip_vpn))

    filas.extend([
        ("Protocolo VPN", acceso.get("protocolo", datos.get("protocolo", "OpenVPN"))),
        ("Host Server", acceso.get("host_server", datos.get("host_server", "dataweb.innovex.cl"))),
        ("Puerto Server", acceso.get("puerto_server", datos.get("puerto_server", "8888")))
    ])

    y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas, col_ratio=0.35, alto_fila=18)
    return y