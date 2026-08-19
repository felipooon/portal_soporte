import json
import re
from certificado.tui.motes import parse_cmd_motes
from certificado.constants.empresas import parse_location_info


def parse_cmd_status(texto: str) -> dict:
    """Extrae datos de la antena a partir de la salida de 'cmd status' o 'pancoordinator status'."""
    res = {}
    for line in texto.splitlines():
        line_s = line.strip()
        # Versión de Firmware / Pancoordinator
        if line_s.lower().startswith("version"):
            partes = line_s.split(maxsplit=1)
            if len(partes) > 1 and not partes[1].lower().startswith("mote") and not partes[1].lower().startswith("microlib"):
                res["version"] = partes[1].strip()
        elif "firmware version" in line_s.lower():
            res["version"] = line_s.split(":", 1)[1].strip()

        # MAC
        if "mac:" in line_s.lower():
            res["mac"] = line_s.split(":", 1)[1].strip()

        # Pan ID
        if "pan id:" in line_s.lower():
            res["panid"] = line_s.split(":", 1)[1].strip()

        # Cantidad de motes / equipos asociados
        m_att = re.search(r"(?:N\s+of\s+motes\s+attached|motes\s+attached|equipos\s+asociados)\s*:\s*(\d+)", line_s, re.IGNORECASE)
        if m_att:
            res["cantidad_equipos_asociados"] = m_att.group(1)

    return res


def parse_kernel(texto: str) -> dict:
    """Extrae la versión del Kernel desde uname -r / uname -a / hostnamectl."""
    res = {}
    in_kernel = False
    for line in texto.splitlines():
        line_strip = line.strip()
        if not line_strip:
            continue

        if "--- KERNEL ---" in line_strip or "=== KERNEL ===" in line_strip:
            in_kernel = True
            continue
        if in_kernel and line_strip.startswith("==="):
            in_kernel = False

        if in_kernel:
            m = re.search(r"([0-9]+\.[0-9]+\.[0-9]+[-0-9a-zA-Z._]+)", line_strip)
            if m:
                res["kernel"] = m.group(1).strip()
                return res

        m_host = re.search(r"Kernel(?:\s*Version)?:\s*(?:Linux\s*)?([0-9]+\.[0-9]+\.[0-9]+[-0-9a-zA-Z._]+)", line_strip, re.I)
        if m_host:
            res["kernel"] = m_host.group(1).strip()
            return res

        m_uname = re.search(r"Linux\s+[a-zA-Z0-9._-]+\s+([0-9]+\.[0-9]+\.[0-9]+[^\s]*)", line_strip)
        if m_uname:
            res["kernel"] = m_uname.group(1).strip()
            return res

        m_generic = re.search(r"\b([0-9]+\.[0-9]+\.[0-9]+-[0-9]+-[a-zA-Z0-9._]+)\b", line_strip)
        if m_generic:
            res["kernel"] = m_generic.group(1).strip()
            return res

    return res


def parse_ifconfig(texto: str) -> dict:
    """
    Extrae interfaz ethernet, MAC ethernet, IP LAN y VPN tun0 desde 'ifconfig'.
    """
    res = {}
    current_iface = ""
    for line in texto.splitlines():
        if line and not line.startswith(" ") and not line.startswith("\t"):
            current_iface = line.split(":")[0].strip()

        if "ether" in line:
            m = re.search(r"ether\s+([0-9a-fA-F:]{11,17})", line)
            if m:
                mac_encontrada = m.group(1)
                if not res.get("mac_ethernet") or current_iface.startswith(("enp", "eth", "eno", "en")):
                    res["mac_ethernet"] = mac_encontrada

        if "inet " in line or "inet\t" in line:
            m = re.search(r"inet\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", line)
            if m:
                ip = m.group(1)
                if current_iface == "tun0":
                    res["tun0"] = ip
                elif ip.startswith("192.168.8."):
                    res["ip_camara_red"] = ip
                elif current_iface and ip != "127.0.0.1":
                    if not res.get("ip_lan") or current_iface.startswith(("enp", "eth", "eno", "en")):
                        res["interfaz"] = current_iface
                        res["ip_lan"] = ip

    return res


def parse_hostnamectl(texto: str) -> dict:
    """
    Extrae hostname, sistema operativo, marca, modelo y categoría desde 'hostnamectl'.
    """
    res = {}
    for line in texto.splitlines():
        line_strip = line.strip()
        if "static hostname:" in line_strip.lower():
            host = line_strip.split(":", 1)[1].strip()
            if host:
                res["location"] = host
                emp, nom_c = parse_location_info(host)
                res["nombre_centro"] = nom_c
                if emp:
                    res["empresa"] = emp

        elif "operating system:" in line_strip.lower():
            res["sistema_operativo"] = line_strip.split(":", 1)[1].strip()

        elif "hardware vendor:" in line_strip.lower():
            vendor = line_strip.split(":", 1)[1].strip()
            if vendor and vendor.lower() != "n/a":
                res["marca"] = vendor

        elif "hardware model:" in line_strip.lower():
            model = line_strip.split(":", 1)[1].strip()
            if model and model.lower() != "n/a":
                res["modelo"] = model

        elif "chassis:" in line_strip.lower() or "icon name:" in line_strip.lower():
            val = line_strip.split(":", 1)[1].strip().lower()
            if any(k in val for k in ("laptop", "notebook")):
                res["categoria"] = "Notebook"
            elif any(k in val for k in ("embedded", "raspberry", "arm")):
                res["categoria"] = "Raspberry Pi"
                res["marca"] = "RPI"
                res["modelo"] = "RPI"

    if res.get("categoria") == "Notebook":
        if "marca" not in res:
            res["marca"] = "Dell Inc."
        if "modelo" not in res:
            res["modelo"] = "Vostro 3405"

    return res


def parse_cacheton_json(texto: str) -> dict:
    """
    Extrae puerto de servidor, location y hostserver desde la configuración JSON o texto plano.
    """
    res = {}
    try:
        match = re.search(r"\{[^{}]*\"portserver\"[^{}]*\}", texto, re.DOTALL)
        json_str = match.group(0) if match else (texto.strip() if "{" in texto else "")
        if json_str:
            data = json.loads(json_str)
            if "portserver" in data:
                res["puerto_server"] = str(data["portserver"])
            if "location" in data:
                loc = str(data["location"])
                res["location"] = loc
                emp, nom_c = parse_location_info(loc)
                res["nombre_centro"] = nom_c
                if emp:
                    res["empresa"] = emp
            if "hostserver" in data:
                res["hostserver"] = str(data["hostserver"])
    except Exception:
        pass

    if "puerto_server" not in res:
        m_port = re.search(r"\"?\bportserver\b\"?\s*[:=]\s*\"?(\d{4})\"?", texto, re.IGNORECASE)
        if m_port:
            res["puerto_server"] = m_port.group(1)

    if "hostserver" not in res:
        m_host = re.search(r"\"?\bhostserver\b\"?\s*[:=]\s*\"?([a-zA-Z0-9.-]+)\"?", texto, re.IGNORECASE)
        if m_host:
            res["hostserver"] = m_host.group(1)

    if "location" not in res:
        m_loc = re.search(r"\"?\blocation\b\"?\s*[:=]\s*\"?([a-zA-Z0-9_-]+)\"?", texto, re.IGNORECASE)
        if m_loc and m_loc.group(1).lower() not in ("cacheton", "data", "localhost"):
            loc = m_loc.group(1)
            res["location"] = loc
            emp, nom_c = parse_location_info(loc)
            res["nombre_centro"] = nom_c
            if emp:
                res["empresa"] = emp

    return res


def procesar_autofill(certificado: dict, texto_pegado: str) -> dict:
    """
    Procesa cualquier fragmento o combinación de salidas de consola
    (cmd status, cmd motes, ifconfig, hostnamectl, JSON config) y actualiza el certificado.
    Retorna un diccionario con el resumen de cambios realizados.
    """
    resumen = []

    # 1. cmd status -> Monitoreo Abiótico
    datos_status = parse_cmd_status(texto_pegado)
    if datos_status:
        if "monitoreo_abiotico" not in certificado:
            certificado["monitoreo_abiotico"] = {}

        mon = certificado["monitoreo_abiotico"]
        mon["instalado"] = "Si"

        if "version" in datos_status:
            mon["version"] = datos_status["version"]
            resumen.append(f"Monitoreo Abiótico -> Versión: {datos_status['version']}")

        if "mac" in datos_status:
            mon["mac"] = datos_status["mac"]
            resumen.append(f"Monitoreo Abiótico -> MAC Antena: {datos_status['mac']}")

        if "panid" in datos_status:
            mon["panid"] = datos_status["panid"]
            resumen.append(f"Monitoreo Abiótico -> Pan ID: {datos_status['panid']}")

        if "cantidad_equipos_asociados" in datos_status:
            mon["cantidad_equipos_asociados"] = datos_status["cantidad_equipos_asociados"]
            resumen.append(f"Monitoreo Abiótico -> Equipos Asociados: {datos_status['cantidad_equipos_asociados']}")

    # 1b. Kernel -> Infraestructura
    datos_kernel = parse_kernel(texto_pegado)
    if datos_kernel and "kernel" in datos_kernel:
        if "infraestructura" not in certificado:
            certificado["infraestructura"] = {}
        certificado["infraestructura"]["kernel"] = datos_kernel["kernel"]
        resumen.append(f"Infraestructura -> Kernel: {datos_kernel['kernel']}")

    # 2. ifconfig -> Infraestructura, Acceso Remoto, Activación
    datos_ifconfig = parse_ifconfig(texto_pegado)
    if datos_ifconfig:
        if "infraestructura" not in certificado:
            certificado["infraestructura"] = {}
        if "acceso_remoto" not in certificado:
            certificado["acceso_remoto"] = {}
        if "activacion" not in certificado:
            certificado["activacion"] = {}

        if "mac_ethernet" in datos_ifconfig:
            certificado["infraestructura"]["mac_ethernet"] = datos_ifconfig["mac_ethernet"]
            resumen.append(f"Infraestructura -> MAC Ethernet: {datos_ifconfig['mac_ethernet']}")

        if "tun0" in datos_ifconfig:
            certificado["acceso_remoto"]["tun0"] = datos_ifconfig["tun0"]
            certificado["infraestructura"]["ip_vpn"] = datos_ifconfig["tun0"]
            resumen.append(f"Acceso Remoto / Infraestructura -> VPN tun0: {datos_ifconfig['tun0']}")

        if "ip_camara_red" in datos_ifconfig:
            if "estacion_camara" not in certificado:
                certificado["estacion_camara"] = {}
            ec = certificado["estacion_camara"]
            ec["camara_instalada"] = "Si"
            ec["tipo_ip_camara"] = "Fija"
            if not ec.get("ip_fija_camara"):
                ec["ip_fija_camara"] = "192.168.8.40"
            resumen.append("Estación y Cámara -> Cámara IP Fija: 192.168.8.40 (detectada red 192.168.8.x)")

        if "ip_lan" in datos_ifconfig:
            certificado["activacion"]["ip_final"] = datos_ifconfig["ip_lan"]
            resumen.append(f"Activación -> IP Observada: {datos_ifconfig['ip_lan']}")

        if "interfaz" in datos_ifconfig:
            certificado["activacion"]["interfaz"] = datos_ifconfig["interfaz"]
            resumen.append(f"Activación -> Interfaz Ethernet: {datos_ifconfig['interfaz']}")

    # 3. hostnamectl -> Infraestructura y Datos Generales
    datos_host = parse_hostnamectl(texto_pegado)
    if datos_host:
        if "infraestructura" not in certificado:
            certificado["infraestructura"] = {}
        if "datos_generales" not in certificado:
            certificado["datos_generales"] = {}

        infra = certificado["infraestructura"]
        dg = certificado["datos_generales"]

        if "sistema_operativo" in datos_host:
            infra["sistema_operativo"] = datos_host["sistema_operativo"]
            resumen.append(f"Infraestructura -> S.O.: {datos_host['sistema_operativo']}")

        if "marca" in datos_host:
            infra["marca"] = datos_host["marca"]
            resumen.append(f"Infraestructura -> Marca: {datos_host['marca']}")

        if "modelo" in datos_host:
            infra["modelo"] = datos_host["modelo"]
            resumen.append(f"Infraestructura -> Modelo: {datos_host['modelo']}")

        if "categoria" in datos_host:
            infra["categoria"] = datos_host["categoria"]
            resumen.append(f"Infraestructura -> Categoría: {datos_host['categoria']}")

        if "location" in datos_host:
            dg["location"] = datos_host["location"]
            dg["nombre_centro"] = datos_host.get("nombre_centro", datos_host["location"].upper())
            if "empresa" in datos_host:
                dg["empresa"] = datos_host["empresa"]
                resumen.append(f"Datos Generales -> Empresa Inferida: {datos_host['empresa']}")
            resumen.append(f"Datos Generales -> Centro / Location: {datos_host['location']}")

    # 4. JSON Config (Cacheton / jenreceiver) -> Acceso Remoto y Datos Generales
    datos_json = parse_cacheton_json(texto_pegado)
    if datos_json:
        if "acceso_remoto" not in certificado:
            certificado["acceso_remoto"] = {}
        if "datos_generales" not in certificado:
            certificado["datos_generales"] = {}

        if "hostserver" in datos_json:
            certificado["acceso_remoto"]["hostserver"] = datos_json["hostserver"]
            resumen.append(f"Acceso Remoto -> Host Server: {datos_json['hostserver']}")

        if "puerto_server" in datos_json:
            certificado["acceso_remoto"]["puerto_server"] = datos_json["puerto_server"]
            resumen.append(f"Acceso Remoto -> Puerto Server: {datos_json['puerto_server']}")

        if "location" in datos_json:
            loc = datos_json["location"]
            certificado["datos_generales"]["location"] = loc
            emp, nom_c = parse_location_info(loc)
            certificado["datos_generales"]["nombre_centro"] = nom_c
            if emp:
                certificado["datos_generales"]["empresa"] = emp
                resumen.append(f"Datos Generales -> Empresa Inferida: {emp}")
            resumen.append(f"Datos Generales -> Location: {loc}")

    # 5. cmd motes -> Listado de Motes / Equipos Jennic
    motes_parseados = parse_cmd_motes(texto_pegado)
    if motes_parseados:
        if "motes" not in certificado or not certificado["motes"]:
            certificado["motes"] = motes_parseados
        else:
            macs_existentes = {m.get("mac", "").upper(): i for i, m in enumerate(certificado["motes"])}
            for m in motes_parseados:
                mac_u = m.get("mac", "").upper()
                if mac_u in macs_existentes:
                    certificado["motes"][macs_existentes[mac_u]].update(m)
                else:
                    certificado["motes"].append(m)
        resumen.append(f"Equipos Jennic -> {len(motes_parseados)} motes importados ({len(certificado['motes'])} total)")

    # 6. Tabla de alarmas por copiar y pegar (TSV/Excel/Texto)
    from certificado.utils.excel_parser import parsear_alarmas_texto
    alarmas_parseadas = parsear_alarmas_texto(texto_pegado)
    if alarmas_parseadas:
        if "configuracion_alarmas" not in certificado or not certificado["configuracion_alarmas"]:
            certificado["configuracion_alarmas"] = alarmas_parseadas
        else:
            for al in alarmas_parseadas:
                if al not in certificado["configuracion_alarmas"]:
                    certificado["configuracion_alarmas"].append(al)
        resumen.append(f"Configuración de Alarmas -> {len(alarmas_parseadas)} alarmas importadas ({len(certificado['configuracion_alarmas'])} total)")

    # 7. Reporte técnico / mensaje WhatsApp del técnico
    from certificado.utils.whatsapp_parser import parsear_mensaje_whatsapp
    datos_wa = parsear_mensaje_whatsapp(texto_pegado)
    if datos_wa:
        dg_wa = datos_wa.get("datos_generales", {})
        if "location" in dg_wa and bool(dg_wa["location"]):
            if "datos_generales" not in certificado:
                certificado["datos_generales"] = {}
            loc = dg_wa["location"]
            certificado["datos_generales"]["location"] = loc
            emp, nom_c = parse_location_info(loc)
            certificado["datos_generales"]["nombre_centro"] = nom_c
            if emp:
                certificado["datos_generales"]["empresa"] = emp
            resumen.append(f"Datos Generales -> Location: {loc}")

        for k in ("puerto_patron", "barrio", "numero_centro", "correo_centro", "coordenadas"):
            if k in dg_wa and bool(dg_wa[k]):
                if "datos_generales" not in certificado:
                    certificado["datos_generales"] = {}
                certificado["datos_generales"][k] = dg_wa[k]
                resumen.append(f"Datos Generales -> {k.replace('_', ' ').title()}: {dg_wa[k]}")

        infra_wa = datos_wa.get("infraestructura", {})
        if infra_wa:
            if "infraestructura" not in certificado:
                certificado["infraestructura"] = {}
            for k, v in infra_wa.items():
                if bool(v):
                    certificado["infraestructura"][k] = v
                    resumen.append(f"Infraestructura -> {k.replace('_', ' ').title()}: {v}")

        ar_wa = datos_wa.get("acceso_remoto", {})
        if ar_wa:
            if "acceso_remoto" not in certificado:
                certificado["acceso_remoto"] = {}
            for k, v in ar_wa.items():
                if bool(v):
                    if k in ("puerto_server", "hostserver") and certificado["acceso_remoto"].get(k):
                        continue
                    certificado["acceso_remoto"][k] = v
                    resumen.append(f"Acceso Remoto -> {k.replace('_', ' ').title()}: {v}")

        act_wa = datos_wa.get("activacion", {})
        if act_wa:
            if "activacion" not in certificado:
                certificado["activacion"] = {}
            for k, v in act_wa.items():
                if bool(v):
                    certificado["activacion"][k] = v
                    resumen.append(f"Activación -> {k.replace('_', ' ').title()}: {v}")

        ec_wa = datos_wa.get("estacion_camara", {})
        if ec_wa:
            if "estacion_camara" not in certificado:
                certificado["estacion_camara"] = {}
            for k, v in ec_wa.items():
                if bool(v):
                    certificado["estacion_camara"][k] = v
                    resumen.append(f"Estación/Cámara -> {k.replace('_', ' ').title()}: {v}")

        ubis_wa = datos_wa.get("ubicaciones", [])
        if ubis_wa:
            if "ubicaciones" not in certificado or not certificado["ubicaciones"]:
                certificado["ubicaciones"] = ubis_wa
            else:
                nombres_existentes = {u.get("nombre", "").lower(): i for i, u in enumerate(certificado["ubicaciones"])}
                for u_new in ubis_wa:
                    nom_l = u_new.get("nombre", "").lower()
                    if nom_l in nombres_existentes:
                        u_old = certificado["ubicaciones"][nombres_existentes[nom_l]]
                        if u_new.get("coordenadas") and not u_old.get("coordenadas"):
                            u_old["coordenadas"] = u_new["coordenadas"]
                        if u_new.get("elementos"):
                            if not u_old.get("elementos"):
                                u_old["elementos"] = u_new["elementos"]
                            else:
                                for el_new in u_new["elementos"]:
                                    if el_new not in u_old["elementos"]:
                                        u_old["elementos"].append(el_new)
                    else:
                        certificado["ubicaciones"].append(u_new)
            resumen.append(f"Ubicaciones -> {len(ubis_wa)} ubicaciones incorporadas ({len(certificado['ubicaciones'])} total)")

        if datos_wa.get("observaciones"):
            obs_nueva = datos_wa["observaciones"]
            if not certificado.get("observaciones"):
                certificado["observaciones"] = obs_nueva
            elif obs_nueva not in certificado["observaciones"]:
                certificado["observaciones"] += f" | {obs_nueva}"
            resumen.append("Observaciones -> Actualizadas desde reporte técnico")

    return {
        "exito": bool(resumen),
        "resumen": resumen
    }
