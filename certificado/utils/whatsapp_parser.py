import re


def parsear_mensaje_whatsapp(texto: str) -> dict:
    """
    Parsea textos de mensajes semi-informales de instalación (vía WhatsApp o reporte técnico)
    con patrones altamente dinámicos y flexibles.
    """
    data = {
        "datos_generales": {},
        "infraestructura": {},
        "acceso_remoto": {},
        "monitoreo_abiotico": {},
        "estacion_camara": {},
        "ubicaciones": [],
        "equipos_repuesto": [],
        "activacion": {},
        "observaciones": ""
    }

    if not texto:
        return data

    lineas_raw = [l.strip() for l in texto.splitlines()]
    lineas = [l for l in lineas_raw if l]

    observaciones_lineas = []
    current_ubicacion = None
    ultimo_sensor_dict = None

    idx = 0
    while idx < len(lineas):
        linea = lineas[idx]
        linea_lower = linea.lower()

        # 1. Identificación del centro / Location
        m_loc = re.search(r"(?:instalación\s+(?:terminada|finalizada)\s+en|location|centro)\s*:?\s*([a-zA-Z0-9_-]+)", linea, re.IGNORECASE)
        if m_loc:
            loc = m_loc.group(1).strip().lower()
            if len(loc) >= 3 and loc not in ("centro", "centros", "equipo", "equipos", "sensor", "sensores"):
                data["datos_generales"]["location"] = loc
                data["datos_generales"]["nombre_centro"] = loc.upper()
                idx += 1
                continue

        # 2. Clave / Contraseña PC
        m_clave = re.search(r"(?:clave|contraseña|pass|password)\s*(?:pc)?:?\s*(.+)", linea, re.IGNORECASE)
        if m_clave:
            data["acceso_remoto"]["clave"] = m_clave.group(1).strip()
            idx += 1
            continue

        # 3. Tide port / Puerto patrón
        m_patron = re.search(r"(?:tide\s*port|puerto\s*patron|puerto\s*patrón):?\s*(.+)", linea, re.IGNORECASE)
        if m_patron:
            data["datos_generales"]["puerto_patron"] = m_patron.group(1).strip()
            idx += 1
            continue

        # 4. Barrio
        m_barrio = re.search(r"barrio\s*:?\s*([a-zA-Z0-9_-]+)", linea, re.IGNORECASE)
        if m_barrio:
            data["datos_generales"]["barrio"] = m_barrio.group(1).strip()
            idx += 1
            continue

        # 5. Celular / Teléfono / Contacto
        m_cel = re.search(r"(?:celular|telefono|tel|contacto|número\s*centro):?\s*(.+)", linea, re.IGNORECASE)
        if m_cel:
            data["datos_generales"]["numero_centro"] = m_cel.group(1).strip()
            idx += 1
            continue

        # 6. Correo centro
        m_correo = re.search(r"(?:correo|email):?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", linea, re.IGNORECASE)
        if m_correo:
            data["datos_generales"]["correo_centro"] = m_correo.group(1).strip()
            idx += 1
            continue

        # 7. IP Fija / LAN / VPN / Tun0
        m_ip = re.search(r"\bip\s*(?:lan|fija)?\s*:?\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", linea, re.IGNORECASE)
        if m_ip:
            ip_val = m_ip.group(1).strip()
            data["activacion"]["tipo_ip"] = "Fija"
            data["activacion"]["ip_fija"] = ip_val
            data["activacion"]["ip_final"] = ip_val
            data["infraestructura"]["ip_lan"] = ip_val
            idx += 1
            continue

        m_tun = re.search(r"tun\s*0\s*:?\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", linea, re.IGNORECASE)
        if m_tun:
            data["acceso_remoto"]["tun0"] = m_tun.group(1).strip()
            data["infraestructura"]["ip_vpn"] = m_tun.group(1).strip()
            idx += 1
            continue

        if "weather" not in linea_lower:
            m_portserver = re.search(r"\bport\s*server\b\s*[:=]?\s*\"?(\d{4})\"?", linea, re.IGNORECASE)
            if not m_portserver:
                m_portserver = re.search(r"^\s*port\s*server\s*:?\s*\"?(\d{4})\"?", linea, re.IGNORECASE)
            if m_portserver:
                data["acceso_remoto"]["puerto_server"] = m_portserver.group(1).strip()
                idx += 1
                continue

        # 8. Conectividad / Puerto
        if "conectado por cable" in linea_lower or "cableada" in linea_lower:
            data["infraestructura"]["conectividad"] = "Cableada"
            m_pto = re.search(r"(?:pto|puerto)\s*(?:número|n°|num)?\s*(\d+)", linea, re.IGNORECASE)
            if m_pto:
                data["infraestructura"]["puerto"] = m_pto.group(1).strip()
            idx += 1
            continue

        # 9. Verificación de Estación Davis / Cámara deshabilitadas
        if re.search(r"no\s+se\s+instala\s+estación", linea_lower) or "sin estacion" in linea_lower:
            data["estacion_camara"]["estacion_instalada"] = "No"
            observaciones_lineas.append(linea)
            idx += 1
            continue

        if re.search(r"no\s+se\s+instala\s+cámara", linea_lower) or "sin camara" in linea_lower:
            data["estacion_camara"]["camara_instalada"] = "No"
            if linea not in observaciones_lineas:
                observaciones_lineas.append(linea)
            idx += 1
            continue

        # 10. Ubicaciones (Pontón / Jaula / Módulo / Balsa)
        ub_match = re.match(r"^(pontón|ponton|módulo\s*jaula\s*\d+|jaula\s*:?\s*\d+|balsa\s*\d+)\s*(.*)$", linea, re.IGNORECASE)
        if ub_match:
            nom_ub = ub_match.group(1).strip()
            if nom_ub.lower() in ("ponton", "pontón"):
                nom_ub = "Pontón Principal"

            rest = ub_match.group(2).strip()
            coords = ""
            m_c = re.search(r"(-?\d{1,2}\.\d+)[\s,]+(-?\d{1,3}\.\d+)", rest)
            if m_c:
                coords = f"{m_c.group(1)} {m_c.group(2)}"
            elif idx + 1 < len(lineas):
                # Revisar si la línea Siguiente tiene las coordenadas
                sig_linea = lineas[idx + 1]
                m_c2 = re.search(r"^(-?\d{1,2}\.\d+)[\s,]+(-?\d{1,3}\.\d+)$", sig_linea.strip())
                if m_c2:
                    coords = f"{m_c2.group(1)} {m_c2.group(2)}"
                    idx += 1  # consumir la línea de coordenadas

            if nom_ub == "Pontón Principal" and coords:
                data["datos_generales"]["coordenadas"] = coords

            current_ubicacion = {"nombre": nom_ub, "coordenadas": coords, "elementos": []}
            data["ubicaciones"].append(current_ubicacion)
            ultimo_sensor_dict = None
            idx += 1
            continue

        # 11. Sensores / Elementos (Name X / Sensor X / Nombre X)
        sensor_head = re.match(r"^name\s*\d+\s*:?\s*(.*)$", linea, re.IGNORECASE)
        if sensor_head:
            detalles = sensor_head.group(1).strip()

            # Extraer metraje de la misma línea o de la siguiente
            metraje = ""
            m_met = re.search(r"(\d+)\s*(?:m|mts|metros)?", detalles, re.IGNORECASE)
            if m_met:
                metraje = m_met.group(1)

            # Extraer parámetro
            param = ""
            if "/" in detalles:
                param = detalles.split("/", 1)[1].strip()
            elif "parametro" in detalles.lower():
                m_p = re.search(r"parametro\s*:?\s*(.+)", detalles, re.IGNORECASE)
                if m_p:
                    param = m_p.group(1).strip()

            if not param and idx + 1 < len(lineas):
                sig_linea = lineas[idx + 1]
                if any(k in sig_linea.lower() for k in ("oxi", "sal", "t°", "temp", "prof", "parametro")):
                    param = sig_linea.strip()
                    idx += 1  # consumir la línea de parámetros

            if "oxi" in param.lower() or "sal" in param.lower():
                param = "Oxi / Sal / T°"

            elem = {
                "tipo": param or "Oxi / Sal / T°",
                "metraje": metraje or "5",
            }

            if not current_ubicacion:
                current_ubicacion = {"nombre": "Pontón", "coordenadas": "", "elementos": []}
                data["ubicaciones"].append(current_ubicacion)

            elementos = current_ubicacion["elementos"]
            if isinstance(elementos, list):
                elementos.append(elem)
            ultimo_sensor_dict = elem
            idx += 1
            continue

        # Si es una línea de parámetro como 'oxi/sal/t°' sola y había un sensor previo sin parámetro
        if ("oxi" in linea_lower or "sal" in linea_lower or "t°" in linea_lower) and ultimo_sensor_dict and not ultimo_sensor_dict.get("tipo"):
            ultimo_sensor_dict["tipo"] = "Oxi / Sal / T°"
            idx += 1
            continue

        # 12. Observaciones / Viñetas / Notas adicionales
        m_obs = re.match(r"^(?:nota|notas|observación|observaciones|obs)\s*:?\s*(.*)$", linea, re.IGNORECASE)
        if m_obs:
            texto_obs = m_obs.group(1).strip()
            if texto_obs:
                observaciones_lineas.append(texto_obs)
            idx += 1
            continue

        es_consola = any(k in linea_lower for k in (
            "cat /", "ifconfig", "hostnamectl", "cmd ", "static hostname:", "inet ", "ether ",
            "flags=", "machine id:", "boot id:", "operating system:", "kernel:", "architecture:",
            "hardware:", "firmware:", "trying 127.", "connected to", "escape character",
            "pancoordinator", "mote ", "rrlog", "crc ", "repeater", "usb-", "innovex@",
            "sudo apt", "chmod", "python", "\"location\":", "\"source\":"
        ))

        if not es_consola and linea.startswith(("•", "*", "-")):
            if not any(k in linea_lower for k in ("artefacto naval", "tipo de red")):
                observaciones_lineas.append(linea.lstrip("•*- ").strip())

        idx += 1

    if observaciones_lineas:
        data["observaciones"] = " ".join(observaciones_lineas)
    else:
        data["observaciones"] = ""

    return data
