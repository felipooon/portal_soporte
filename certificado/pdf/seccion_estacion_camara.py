from .plantilla import (
    MARGEN_X, dibujar_titulo_seccion, dibujar_subtitulo,
    dibujar_tabla_atributo_valor, dibujar_tabla_listado
)


def agregar_estacion_camara(pdf, datos_estacion, datos_monitoreo, y):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "3. Antena, estación meteorológica y cámara")

    ab_instalado = datos_monitoreo.get("instalado", "Si")

    # 3.1 Antena receptora (Monitoreo Abiótico)
    if ab_instalado != "No":
        ubicacion_antena = datos_monitoreo.get("ubicacion_antena") or datos_monitoreo.get("ubicacion") or "Púlpito / Techo"
        y = dibujar_subtitulo(pdf, MARGEN_X, y, "Antena receptora (Monitoreo Abiótico)")
        filas_antena = [
            ("Tipo Antena", datos_monitoreo.get("tipo_antena", "Outdoor")),
            ("Ubicación", ubicacion_antena),
            ("Versión Firmware", datos_monitoreo.get("version", "-")),
            ("MAC", datos_monitoreo.get("mac", "-")),
            ("PAN ID", datos_monitoreo.get("panid", "-")),
            ("Equipos Asociados", str(datos_monitoreo.get("cantidad_equipos_asociados", "-")))
        ]
        y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas_antena, col_ratio=0.35, alto_fila=18)

    # 3.2 Estación meteorológica, cámara y switch PoE
    y = dibujar_subtitulo(pdf, MARGEN_X, y, "Estación meteorológica, cámara y switch PoE")

    cabeceras = ["Elemento", "Estado / tipo", "Detalles (ID / MAC / Modelo)", "Ubicación / Altura"]

    est_inst = str(datos_estacion.get("estacion_instalada", "No")).strip()
    cam_inst = str(datos_estacion.get("camara_instalada", "No")).strip()
    sw_poe = str(datos_estacion.get("switch_poe", "No")).strip()

    conexion_cam = datos_estacion.get("conexion_camara", "")
    if cam_inst != "Si" or (conexion_cam and conexion_cam != "Switch PoE"):
        sw_poe = "No"

    est_modelo = datos_estacion.get("modelo_estacion", "-")
    if est_inst == "Si":
        id_est = datos_estacion.get("id_estacion_meteorologica", "")
        detalles_est = f"Modelo: {est_modelo}" + (f" | ID: {id_est}" if id_est else "")
        alt_est = datos_estacion.get("altura_estacion", "")
        ub_est = datos_estacion.get("ubicacion_estacion", "-") + (f" (Altura: {alt_est}m)" if alt_est else "")
    else:
        detalles_est = "-"
        ub_est = "-"

    if cam_inst == "Si":
        cam_modelo = datos_estacion.get("modelo_camara", "-")
        mac_cam = datos_estacion.get("mac_camara", "")
        detalles_cam = f"Modelo: {cam_modelo}" + (f" | MAC: {mac_cam}" if mac_cam else "")
        ub_cam = datos_estacion.get("ubicacion_camara", "-")
    else:
        detalles_cam = "-"
        ub_cam = "-"

    filas_equipos = [
        ["Estación meteorológica", est_inst, detalles_est, ub_est],
        ["Cámara", cam_inst, detalles_cam, ub_cam],
        [
            "Switch PoE",
            sw_poe,
            datos_estacion.get("modelo_switch", "-") if sw_poe == "Si" else "-",
            datos_estacion.get("ubicacion_switch", "-") if sw_poe == "Si" else "-"
        ]
    ]

    y = dibujar_tabla_listado(
        pdf, MARGEN_X, y, cabeceras, filas_equipos,
        anchos_relativos=[0.25, 0.15, 0.35, 0.25],
        alto_fila=18
    )

    return y
