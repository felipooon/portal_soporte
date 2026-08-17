from .plantilla import (
    MARGEN_X, dibujar_titulo_seccion, dibujar_subtitulo, dibujar_tabla_listado,
    dibujar_tabla_atributo_valor
)


def agregar_equipos_instalados(pdf, ubicaciones, repuestos, y, certificado=None):
    y = dibujar_titulo_seccion(pdf, MARGEN_X, y, "4. Equipos instalados por ubicación")

    cabeceras_eq = ["N°", "Equipo / Elemento", "Identificación (MAC / S/N)", "Sensores Asociados (Tipo — Metros)"]
    anchos_eq = [0.08, 0.32, 0.28, 0.32]

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
                    nombre_eq = elem.get("nombre", "") or elem.get("name", "")
                    label_eq = f"{nombre_eq} ({tipo})" if nombre_eq and tipo != "-" else tipo
                    mac_s = elem.get("mac", "") or elem.get("numero_serie") or elem.get("serie", "") or "-"
                    sensores = elem.get("sensores", [])
                    metraje_legacy = elem.get("metraje", "")
                else:
                    tipo = getattr(elem, "tipo", "") or getattr(elem, "descripcion", "") or "-"
                    nombre_eq = getattr(elem, "nombre", "") or getattr(elem, "name", "")
                    label_eq = f"{nombre_eq} ({tipo})" if nombre_eq and tipo != "-" else tipo
                    mac_s = getattr(elem, "mac", "") or getattr(elem, "numero_serie", "") or getattr(elem, "serie", "") or "-"
                    sensores = getattr(elem, "sensores", []) or []
                    metraje_legacy = getattr(elem, "metraje", "") or ""

                if sensores:
                    def m_key(s):
                        try:
                            m_val = str(s.get("metros", "") if isinstance(s, dict) else getattr(s, "metros", "")).replace("m", "").strip()
                            return float(m_val) if m_val else 0.0
                        except Exception:
                            return 0.0

                    sensores_ord = sorted(sensores, key=m_key)
                    sensores_str_list = []
                    for s in sensores_ord:
                        if isinstance(s, dict):
                            t_s = s.get("tipo_sensor") or s.get("tipo") or "Sensor"
                            m_s = s.get("metros", "")
                        else:
                            t_s = getattr(s, "tipo_sensor", "") or getattr(s, "tipo", "Sensor")
                            m_s = getattr(s, "metros", "")
                        m_lbl = f" ({m_s}m)" if m_s else ""
                        sensores_str_list.append(f"{t_s}{m_lbl}")
                    sensores_str = "\n".join(sensores_str_list)
                elif metraje_legacy:
                    sensores_str = f"Metros: {metraje_legacy}m"
                else:
                    sensores_str = "-"

                filas_loc.append([
                    str(idx),
                    label_eq,
                    mac_s,
                    sensores_str
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
