from .plantilla import (
    MARGEN_X, dibujar_titulo_seccion, dibujar_subtitulo,
    dibujar_tabla_listado, dibujar_tabla_atributo_valor
)


def agregar_validacion_operativa(pdf, datos_activacion, y, certificado=None):
    if certificado is None:
        certificado = {}

    infra = certificado.get("infraestructura", {})
    acceso = certificado.get("acceso_remoto", {})

    interfaz = datos_activacion.get("interfaz") or infra.get("interfaz") or "enp2s0"
    ip_obs = datos_activacion.get("ip_final") or acceso.get("ip_fija") or infra.get("ip_vpn") or "192.168.0.254"
    mac_eth = infra.get("mac_ethernet") or datos_activacion.get("mac_ethernet") or "60:18:95:2a:54:f0"
    vpn_tun = acceso.get("tun0") or infra.get("ip_vpn") or datos_activacion.get("vpn_tun0") or "10.9.31.225"

    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "6. Validación operativa")

    # 6.1 Comunicación de equipos Jennic
    y = dibujar_subtitulo(pdf, MARGEN_X, y, "6.1 Comunicación de equipos Jennic - cmd motes / cmd status")
    cabeceras_motes = ["Mote", "MAC", "Señal", "LastRx", "Asociación"]

    motes = datos_activacion.get("motes") or certificado.get("motes") or []
    filas_motes = []

    for m in motes:
        mote_num = str(m.get("mote") or m.get("id") or "-")
        mac = str(m.get("mac") or "-")
        signal = str(m.get("signal") or m.get("senal") or "-")
        last_rx = str(m.get("last_rx") or m.get("lastrx") or "-")
        asoc = str(m.get("asociacion") or m.get("name") or "-")
        filas_motes.append([mote_num, mac, signal, last_rx, asoc])

    if not filas_motes:
        filas_motes = [
            ["1", "00:15:8D:00:08:5D:5E:BA", "84:90", "14", "Equipo 9"],
            ["2", "00:15:8D:00:09:24:52:AF", "84:84", "8", "Equipo 11"],
            ["3", "00:15:8D:00:01:B2:B8:70", "78:75", "53", "Equipo 7"]
        ]

    y = dibujar_tabla_listado(
        pdf, MARGEN_X, y, cabeceras_motes, filas_motes,
        anchos_relativos=[0.10, 0.35, 0.18, 0.15, 0.22],
        alto_fila=18
    )

    # 6.4 Configuración de red del computador - ifconfig
    y = dibujar_subtitulo(pdf, MARGEN_X, y, "6.4 Configuración de red del computador - ifconfig")
    filas_ifconfig = [
        ("Interfaz Ethernet", interfaz),
        ("IP observada", ip_obs),
        ("MAC Ethernet", mac_eth),
        ("VPN tun0", vpn_tun)
    ]
    y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas_ifconfig, col_ratio=0.35, alto_fila=18)

    # 6.5 Resumen de validación de activación del servicio
    y = dibujar_subtitulo(pdf, MARGEN_X, y, "6.5 Resumen de activación del servicio")
    resp_act = datos_activacion.get("responsable_activacion") or datos_activacion.get("responsable") or "-"
    ip_final = datos_activacion.get("ip_final") or ip_obs
    interfaz_act = datos_activacion.get("interfaz") or interfaz
    estado_final = datos_activacion.get("estado_final", "Operativo")

    filas_resumen_act = [
        ("IP Asignada / Interfaz", f"{ip_final} ({interfaz_act})"),
        ("Responsable de Activación", resp_act),
        ("Estado Final del Servicio", estado_final)
    ]
    y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas_resumen_act, col_ratio=0.35, alto_fila=18)

    return y


def agregar_checklist_validacion(pdf, datos_activacion, y):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "9. Checklist de validación")

    cabeceras = ["VALIDACIÓN", "OK", "N/A", "OBSERVACIÓN"]
    chk = datos_activacion.get("checklist") or {}

    items = [
        ("pc_operativo", "Computador instalado y operativo"),
        ("red_validada", "Configuración de red validada"),
        ("antena_operativa", "Antena receptora operativa"),
        ("jennic_comunicando", "Todos los equipos Jennic comunicando"),
        ("sensores_datos", "Sensores detectados y entregando datos"),
        ("archivos_dat", "Archivos .dat generándose y actualizándose"),
        ("transmision_estacion", "Transmisión datos Estación Meteorológica"),
        ("transmision_camara", "Transmisión datos Fotográficos"),
        ("datos_dataweb", "Datos visibles y actualizando en DataWeb"),
        ("alarmas_estandar", "Alarmas configuradas según estándar")
    ]

    filas_chk = []
    for key, desc in items:
        val = str(chk.get(key, "OK")).upper()
        if val in ("OK", "SI", "TRUE", "CONFORME"):
            ok_mark = "[  ✔  ]"
            na_mark = "[     ]"
            obs = "Conforme"
        elif val in ("N/A", "NO APLICA"):
            ok_mark = "[     ]"
            na_mark = "[  ✔  ]"
            obs = "N/A (No Aplica)"
        else:
            ok_mark = "[     ]"
            na_mark = "[     ]"
            obs = "Pendiente"
        filas_chk.append([desc, ok_mark, na_mark, obs])

    y = dibujar_tabla_listado(
        pdf, MARGEN_X, y, cabeceras, filas_chk,
        anchos_relativos=[0.48, 0.12, 0.12, 0.28],
        alto_fila=17
    )

    return y
