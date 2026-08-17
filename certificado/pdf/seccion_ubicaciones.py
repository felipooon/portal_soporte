from .plantilla import (
    MARGEN_X, dibujar_titulo_seccion, dibujar_subtitulo, dibujar_tabla_listado,
    dibujar_tabla_atributo_valor
)


def agregar_equipos_instalados(pdf, ubicaciones, repuestos, y, certificado=None):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "4. Equipos instalados por ubicación")

    cabeceras_eq = ["N°", "Tipo de elemento", "Metraje", "MAC / N° de serie"]
    anchos_eq = [0.08, 0.42, 0.20, 0.30]

    if not ubicaciones:
        filas_vacias = [["1", "Sin ubicaciones registradas", "-", "-"]]
        y = dibujar_tabla_listado(
            pdf, MARGEN_X, y, cabeceras_eq, filas_vacias,
            anchos_relativos=anchos_eq, alto_fila=18
        )
    else:
        for ub in ubicaciones:
            if isinstance(ub, dict):
                nom_ub = ub.get("nombre", "")
                coords = ub.get("coordenadas", "")
                elementos = ub.get("elementos", [])
            else:
                nom_ub = getattr(ub, "nombre", "")
                coords = getattr(ub, "coordenadas", "")
                elementos = getattr(ub, "elementos", [])

            coords_lbl = f" (GPS: {coords})" if coords and coords != "-" else ""
            subt = f"Ubicación: {nom_ub}{coords_lbl}"
            y = dibujar_subtitulo(pdf, MARGEN_X, y, subt)

            filas_loc = []
            for idx, elem in enumerate(elementos, start=1):
                if isinstance(elem, dict):
                    tipo = elem.get("tipo", "") or elem.get("descripcion", "") or "-"
                    metraje = elem.get("metraje", "")
                    prof = f"{metraje} m" if metraje else "-"
                    mac_s = elem.get("mac", "") or elem.get("numero_serie") or elem.get("serie", "") or "-"
                else:
                    tipo = getattr(elem, "tipo", "") or getattr(elem, "descripcion", "") or "-"
                    metraje = getattr(elem, "metraje", "") or ""
                    prof = f"{metraje} m" if metraje else "-"
                    mac_s = getattr(elem, "mac", "") or getattr(elem, "numero_serie", "") or getattr(elem, "serie", "") or "-"

                filas_loc.append([
                    str(idx),
                    tipo,
                    prof,
                    mac_s
                ])

            if not filas_loc:
                filas_loc = [["1", "Sin equipos instalados en esta ubicación", "-", "-"]]

            y = dibujar_tabla_listado(
                pdf, MARGEN_X, y, cabeceras_eq, filas_loc,
                anchos_relativos=anchos_eq, alto_fila=18
            )

    # 5. Equipos de repuesto
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "5. Equipos de repuesto")

    cabeceras_rep = ["Descripción / Tipo", "MAC / S/N"]
    filas_rep = []
    ubicacion_destacada = ""

    if certificado and isinstance(certificado, dict):
        ubicacion_destacada = certificado.get("ubicacion_repuestos", "")

    for rep in repuestos:
        if isinstance(rep, dict):
            desc = rep.get("tipo") or rep.get("descripcion") or "-"
            metraje = rep.get("metraje", "")
            mac = rep.get("mac", "")
            serie = rep.get("serie") or rep.get("numero_serie") or rep.get("identificacion", "")
            ubi = rep.get("ubicacion") or ""
        else:
            desc = getattr(rep, "tipo", "") or getattr(rep, "descripcion", "") or "-"
            metraje = getattr(rep, "metraje", "") or ""
            mac = getattr(rep, "mac", "")
            serie = getattr(rep, "serie", "") or getattr(rep, "numero_serie", "") or getattr(rep, "identificacion", "") or ""
            ubi = getattr(rep, "ubicacion", "") or ""

        if metraje and not desc.lower().endswith("m"):
            desc = f"{desc} {metraje} m"

        if mac:
            ident_lbl = f"MAC {mac}"
        elif serie:
            ident_lbl = f"Serie {serie}"
        else:
            ident_lbl = "-"

        if ubi and not ubicacion_destacada:
            ubicacion_destacada = ubi

        filas_rep.append([desc, ident_lbl])

    if not filas_rep:
        filas_rep = [["-", "-"]]

    if not ubicacion_destacada:
        ubicacion_destacada = "Sin especificar"

    y = dibujar_tabla_listado(
        pdf, MARGEN_X, y, cabeceras_rep, filas_rep,
        anchos_relativos=[0.55, 0.45],
        alto_fila=18
    )

    # Bloque pegado al pie de la tabla con la Ubicación de los repuestos
    filas_ubi = [("Ubicación de repuestos", ubicacion_destacada)]
    y = dibujar_tabla_atributo_valor(pdf, MARGEN_X, y, filas_ubi, col_ratio=0.30, alto_fila=18)

    return y
