from .plantilla import (
    MARGEN_X, dibujar_titulo_seccion, dibujar_subtitulo,
    dibujar_tabla_atributo_valor, dibujar_tabla_listado
)


def agregar_estacion_camara(pdf, datos_estacion, datos_monitoreo, y):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "3. Antena, estación meteorológica y cámara")

    ubicacion_antena = datos_monitoreo.get("ubicacion_antena") or datos_monitoreo.get("ubicacion") or "Púlpito / Techo"

    # 3.1 Antena receptora
    y = dibujar_subtitulo(pdf, MARGEN_X, y, "Antena receptora")
    filas_antena = [
        ("Tipo", datos_monitoreo.get("tipo_antena", "Outdoor")),
        ("Ubicación", ubicacion_antena),
        ("Versión Jennic", datos_monitoreo.get("version", "-")),
        ("MAC", datos_monitoreo.get("mac", "-")),
        ("PAN ID", datos_monitoreo.get("panid", "-"))
    ]
    y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas_antena, col_ratio=0.35, alto_fila=18)

    # 3.2 Estación meteorológica, cámara y switch PoE
    y = dibujar_subtitulo(pdf, MARGEN_X, y, "Estación meteorológica, cámara y switch PoE")

    cabeceras = ["Elemento", "Estado / tipo", "Modelo", "Ubicación"]

    est_inst = str(datos_estacion.get("estacion_instalada", "No")).strip()
    cam_inst = str(datos_estacion.get("camara_instalada", "No")).strip()
    sw_poe = str(datos_estacion.get("switch_poe", "No")).strip()

    # Si la conexión de la cámara no es Switch PoE o no hay cámara instalada, forzar Switch PoE a 'No'
    conexion_cam = datos_estacion.get("conexion_camara", "")
    if cam_inst != "Si" or (conexion_cam and conexion_cam != "Switch PoE"):
        sw_poe = "No"

    filas_equipos = [
        [
            "Estación meteorológica",
            est_inst,
            datos_estacion.get("modelo_estacion", "-") if est_inst == "Si" else "-",
            datos_estacion.get("ubicacion_estacion", "-") if est_inst == "Si" else "-"
        ],
        [
            "Cámara",
            cam_inst,
            datos_estacion.get("modelo_camara", "-") if cam_inst == "Si" else "-",
            datos_estacion.get("ubicacion_camara", "-") if cam_inst == "Si" else "-"
        ],
        [
            "Switch PoE",
            sw_poe,
            datos_estacion.get("modelo_switch", "-") if sw_poe == "Si" else "-",
            datos_estacion.get("ubicacion_switch", "-") if sw_poe == "Si" else "-"
        ]
    ]

    y = dibujar_tabla_listado(
        pdf, MARGEN_X, y, cabeceras, filas_equipos,
        anchos_relativos=[0.30, 0.20, 0.25, 0.25],
        alto_fila=18
    )

    return y
