from pathlib import Path
from .plantilla import (
    MARGEN_X, dibujar_titulo_seccion, dibujar_tabla_listado
)
from certificado.utils.excel_parser import parsear_alarmas_excel, limpiar_sensor_texto, normalizar_alarma_dict
from certificado.services.certificado_service import CertificadoService


def agregar_configuracion_alarmas(pdf, certificado, y):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "7. Configuración de alarmas")

    alarmas = certificado.get("configuracion_alarmas") or certificado.get("alarmas") or []

    # Si no hay alarmas registradas explícitamente en el certificado,
    # intentar buscar de forma transparente un archivo .ods o .xlsx en evidencias
    if not alarmas:
        datos_gen = certificado.get("datos_generales", {})
        location = datos_gen.get("location") or datos_gen.get("nombre_centro", "ca-ahoni")
        año = 2026

        dir_entrada = Path.home() / "evidencias_instalacion"
        archivos_planillas = [f for f in dir_entrada.iterdir() if f.is_file() and f.suffix.lower() in [".ods", ".xlsx"] and not f.name.startswith(".")] if dir_entrada.exists() else []

        if not archivos_planillas:
            carpeta_ev = CertificadoService.obtener_carpeta_evidencias(location, año)
            archivos_planillas = [f for f in carpeta_ev.iterdir() if f.is_file() and f.suffix.lower() in [".ods", ".xlsx"] and not f.name.startswith(".")]

        if archivos_planillas:
            alarmas = parsear_alarmas_excel(archivos_planillas[0], nombre_centro=datos_gen.get("nombre_centro"))

    cabeceras = ["Status", "Equipo", "Sensor", "Usuario", "Conf. Mín.", "Conf. Máx.", "Medición", "Envío"]
    filas = []

    for al_raw in alarmas:
        al = al_raw if isinstance(al_raw, dict) else (al_raw.__dict__ if hasattr(al_raw, "__dict__") else {})
        al_norm = normalizar_alarma_dict(al)

        status = str(al_norm.get("status", "Activo"))
        equipo = str(al_norm.get("equipo", "-"))
        sensor = str(al_norm.get("sensor", "-"))
        correo = str(al_norm.get("correo", "-"))
        conf_min = str(al_norm.get("conf_min", "-"))
        conf_max = str(al_norm.get("conf_max", "-"))
        medicion = str(al_norm.get("medicion", "-"))
        envio = str(al_norm.get("envio", "60"))

        filas.append([status, equipo, sensor, correo, conf_min, conf_max, medicion, envio])

    if not filas:
        filas = [["-", "-", "Sin alarmas configuradas", "-", "-", "-", "-", "-"]]

    y = dibujar_tabla_listado(
        pdf, MARGEN_X, y, cabeceras, filas,
        anchos_relativos=[0.09, 0.12, 0.28, 0.22, 0.08, 0.08, 0.08, 0.05],
        alto_fila=18
    )

    return y
