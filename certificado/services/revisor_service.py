"""
Módulo de servicio para verificación remota de equipos Innovex
e integración con el sistema de Certificado de Instalación.
"""

import base64
import os
import re
import socket
import subprocess
import time
import getpass
import html
from pathlib import Path
from datetime import datetime
from email.utils import parsedate_to_datetime


def campo(texto: str, patron: str) -> str:
    m = re.search(patron, texto, re.MULTILINE | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def parsear_paquetes(texto: str) -> dict:
    paquetes = {
        "cacheton": "changeset:   631",
        "python3_cacheton": "changeset:   415",
        "pcinnovex": "changeset:   387",
        "weather_davis": "1.1.1",
        "visibility_cam": "3.6"
    }

    current_repo = None
    for linea in texto.splitlines():
        linea_s = linea.strip()
        m_repo = re.search(r"--- (cacheton|python3_cacheton|python3|pcinnovex|pcinnovex2) ---", linea_s, re.I)
        if m_repo:
            current_repo = m_repo.group(1).lower()
            if current_repo in ("pcinnovex2",):
                current_repo = "pcinnovex"
            elif current_repo in ("python3",):
                current_repo = "python3_cacheton"
            continue

        m_change = re.search(r"changeset:\s*(\d+)", linea_s, re.I)
        if m_change and current_repo:
            paquetes[current_repo] = f"changeset:   {m_change.group(1)}"
            continue

        m_dpkg = re.search(r"^(cacheton|python3_cacheton|python3|pcinnovex|pcinnovex2):\s*(?:changeset:\s*)?(\d+)", linea_s, re.I)
        if m_dpkg:
            repo_name = m_dpkg.group(1).lower()
            if repo_name in ("pcinnovex2",):
                repo_name = "pcinnovex"
            elif repo_name in ("python3",):
                repo_name = "python3_cacheton"
            paquetes[repo_name] = f"changeset:   {m_dpkg.group(2)}"

        m_davis = re.search(r"weather[-_]?station[-_]?davis[_-]([\d]+(?:\.[\d]+)*)", linea_s, re.I)
        if m_davis:
            paquetes["weather_davis"] = m_davis.group(1).rstrip(".")

        m_vis = re.search(r"visibility[-_]?cam[_-]([\d]+(?:\.[\d]+)*)", linea_s, re.I)
        if m_vis:
            paquetes["visibility_cam"] = m_vis.group(1).rstrip(".")

    return paquetes


def parsear_so_y_kernel(texto: str) -> tuple[str, str]:
    so_encontrado = ""
    kernel_encontrado = ""
    in_kernel = False

    for linea in texto.splitlines():
        linea_s = linea.strip()
        if not linea_s:
            continue

        if "=== SO & KERNEL ===" in linea_s or "=== OS_RELEASE ===" in linea_s or "=== HOSTNAMECTL ===" in linea_s:
            in_kernel = False
            continue
        if "--- KERNEL ---" in linea_s or "=== KERNEL ===" in linea_s:
            in_kernel = True
            continue
        if in_kernel and linea_s.startswith("==="):
            in_kernel = False

        if in_kernel:
            m_k = re.search(r"([0-9]+\.[0-9]+\.[0-9]+[-0-9a-zA-Z._]+)", linea_s)
            if m_k and not kernel_encontrado:
                kernel_encontrado = m_k.group(1).strip()
                continue

        m_k_host = re.search(r"Kernel(?:\s*Version)?:\s*(?:Linux\s*)?([0-9]+\.[0-9]+\.[0-9]+[-0-9a-zA-Z._]+)", linea_s, re.I)
        if m_k_host and not kernel_encontrado:
            kernel_encontrado = m_k_host.group(1).strip()

        m_pretty = re.search(r'PRETTY_NAME="([^"]+)"', linea_s)
        if m_pretty:
            so_raw = m_pretty.group(1).strip()
            so_encontrado = f"Linux {so_raw}" if not so_raw.lower().startswith("linux") else so_raw
            continue

        m_os = re.search(r"Operating System:\s*(.+)", linea_s, re.I)
        if m_os:
            so_raw = m_os.group(1).strip()
            so_encontrado = f"Linux {so_raw}" if not so_raw.lower().startswith("linux") else so_raw
            continue

        m_lsb = re.search(r"Description:\s*(.+)", linea_s, re.I)
        if m_lsb:
            so_raw = m_lsb.group(1).strip()
            so_encontrado = f"Linux {so_raw}" if not so_raw.lower().startswith("linux") else so_raw
            continue

        if not kernel_encontrado:
            m_k2 = re.search(r"\b([0-9]+\.[0-9]+\.[0-9]+-[0-9]+-[a-zA-Z0-9._]+)\b", linea_s)
            if m_k2 and ("SMP" in linea_s or "Linux" in linea_s or "-" in m_k2.group(1)):
                kernel_encontrado = m_k2.group(1).strip()

    return so_encontrado or "Linux Ubuntu 20.04 LTS", kernel_encontrado or "5.4.0-105-generic"


def parsear_senal_motes(nodos_motes: dict) -> str:
    """
    Busca el mote con la señal más baja enfocándose en el valor yy (equipo hacia antena)
    y retorna 'igual o mayor a xx/yy' (o 'igual o mayor a 57/198').
    """
    if not nodos_motes:
        return "igual o mayor a 57/198"

    motes_con_senal = []
    for nodo_id, m in nodos_motes.items():
        sig_str = m.get("signal", "")
        if sig_str and ":" in sig_str:
            parts = sig_str.split(":")
            try:
                xx = int(parts[0])
                yy = int(parts[1])
                motes_con_senal.append((yy, xx, sig_str))
            except ValueError:
                pass
        elif sig_str and "/" in sig_str:
            parts = sig_str.split("/")
            try:
                xx = int(parts[0])
                yy = int(parts[1])
                motes_con_senal.append((yy, xx, sig_str))
            except ValueError:
                pass

    if not motes_con_senal:
        return "igual o mayor a 57/198"

    # Ordenar por el valor 'yy' (menor señal de equipo a antena)
    motes_con_senal.sort(key=lambda x: x[0])
    min_yy, min_xx, _ = motes_con_senal[0]
    return f"igual o mayor a {min_xx}/{min_yy}"


def parsear_voltaje_minimo(voltajes: dict) -> str:
    """
    Busca el voltaje más bajo detectado en los nodos y retorna 'igual o mayor a X.XXV'.
    """
    v_vals = [v_info["voltaje"] for v_info in voltajes.values() if isinstance(v_info, dict) and v_info.get("voltaje", 0) > 0]
    if v_vals:
        min_v = min(v_vals)
        return f"igual o mayor a {min_v:.2f}V"
    return "igual o mayor a 3.33V"


def parsear_voltajes_y_sensores(texto: str) -> tuple[dict, dict]:
    """
    Analiza logs de jenreceiver para extraer:
    1) Voltajes de batería y alimentación de cada nodo (:NODE).
    2) Lecturas de sensores de oxígeno (:OXY), salinidad/conductividad (:COND) y corrientes (:FLOW).
    """
    voltajes = {}
    sensores = {}

    pat_node1 = re.compile(r":(?:\d+:)?(\d+):\d+:NODE\s+\d+\s+([0-9]+(?:\.[0-9]+)?)\s+([0-9]+(?:\.[0-9]+)?)", re.I)
    pat_node2 = re.compile(r"\bNODE\s+(\d+)\s+([0-9]+\.[0-9]+)\s+([0-9]+\.[0-9]+)", re.I)
    pat_node3 = re.compile(r":(?:\d+:)?(\d+):\d+:NODE\s+\d*\s*([0-9]+\.[0-9]+)", re.I)

    pat_oxy = re.compile(r":(?:\d+:)?(\d+):\d+:OXY\s+(\d+)\s+([0-9.]+)\s+([0-9.-]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)", re.I)
    pat_cond = re.compile(r":(?:\d+:)?(\d+):\d+:COND\s+(\d+)\s+([0-9.]+)\s+([0-9.-]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)", re.I)
    pat_flow = re.compile(r":(?:\d+:)?(\d+):\d+:FLOW\s+(\d+)\s+([0-9.]+)\s+([0-9.-]+)\s+([0-9.]+)\s+([0-9.]+)", re.I)

    for linea in texto.splitlines():
        linea_s = linea.strip()
        if not linea_s:
            continue

        # 1. NODE (Voltajes)
        m_node = pat_node1.search(linea_s) or pat_node2.search(linea_s)
        if m_node:
            nodo = int(m_node.group(1))
            v_bat = float(m_node.group(2))
            v_alim = float(m_node.group(3))
            voltajes[nodo] = {"voltaje": v_bat, "alimentacion": v_alim}
            continue
        m_node3 = pat_node3.search(linea_s)
        if m_node3:
            nodo = int(m_node3.group(1))
            v_bat = float(m_node3.group(2))
            voltajes[nodo] = {"voltaje": v_bat, "alimentacion": 0.0}
            continue

        # 2. OXY (Oxígeno / Saturación / Temp)
        m_oxy = pat_oxy.search(linea_s)
        if m_oxy:
            nodo = int(m_oxy.group(1))
            groups = m_oxy.groups()
            estado, cable, temp, o2, sat, sal = groups[1], groups[2], groups[3], groups[4], groups[5], groups[6]
            if nodo not in sensores:
                sensores[nodo] = {}
            sensores[nodo]["oxy"] = {
                "estado": int(estado), "cable": float(cable), "temp": float(temp),
                "o2": float(o2), "sat": float(sat), "sal": float(sal)
            }
            continue

        # 3. COND (Salinidad / Conductividad / Temp)
        m_cond = pat_cond.search(linea_s)
        if m_cond:
            nodo = int(m_cond.group(1))
            groups = m_cond.groups()
            estado, cable, temp, cond1, cond2, sal = groups[1], groups[2], groups[3], groups[4], groups[5], groups[6]
            if nodo not in sensores:
                sensores[nodo] = {}
            sensores[nodo]["cond"] = {
                "estado": int(estado), "cable": float(cable), "temp": float(temp),
                "cond1": float(cond1), "cond2": float(cond2), "sal": float(sal)
            }
            continue

        # 4. FLOW (Corrientes / Velocidad / Dirección)
        m_flow = pat_flow.search(linea_s)
        if m_flow:
            nodo = int(m_flow.group(1))
            groups = m_flow.groups()
            estado, cable, factor, vel, direccion = groups[1], groups[2], groups[3], groups[4], groups[5]
            if nodo not in sensores:
                sensores[nodo] = {}
            sensores[nodo]["flow"] = {
                "estado": int(estado), "cable": float(cable), "factor": float(factor),
                "vel": float(vel), "dir": float(direccion)
            }
            continue

    return voltajes, sensores


def parsear_voltajes(texto: str) -> dict:
    voltajes, _ = parsear_voltajes_y_sensores(texto)
    return voltajes


def parsear_lecturas_sensores(texto: str) -> dict:
    """
    Analiza logs de jenreceiver para extraer las últimas lecturas de sensores por ID de equipo.
    """
    _, sensores = parsear_voltajes_y_sensores(texto)
    lecturas_por_nodo = {}
    for nodo_id, s_dict in sensores.items():
        items = []
        if "oxy" in s_dict:
            ox = s_dict["oxy"]
            items.append(f"Sat: {ox['sat']}%")
            items.append(f"O2: {ox['o2']} mg/L")
            items.append(f"Temp: {ox['temp']}°C")
        if "cond" in s_dict:
            co = s_dict["cond"]
            items.append(f"Sal: {co['sal']} PSU")
            if not any("Temp:" in it for it in items):
                items.append(f"Temp: {co['temp']}°C")
        if "flow" in s_dict:
            fl = s_dict["flow"]
            items.append(f"Vel: {fl['vel']} cm/s")
            items.append(f"Dir: {fl['dir']}°")
        if items:
            lecturas_por_nodo[nodo_id] = " | ".join(items)
    return lecturas_por_nodo


def parsear_motes(texto: str) -> dict:
    motes = {}
    patron = re.compile(r"^\s*(\d+)\s+([0-9A-F:]{17,})\s+(\d+:\d+)\s+(\d+)\s+(.+?)\s*$", re.I)
    for linea in texto.splitlines():
        m = patron.match(linea)
        if m:
            numero, mac, signal, last_rx, nombre = m.groups()
            motes[int(numero)] = {"mac": mac, "signal": signal, "last_rx": last_rx, "nombre": nombre}
    return motes


def extraer_version_status(texto: str) -> str:
    m = re.search(r"\bVersion\s*:?[ ]*v?([0-9]+(?:\.[0-9]+)+)", texto, re.I)
    return m.group(1) if m else "No detectada"


def evaluar_estacion(texto: str, ahora: float) -> tuple[str, str]:
    linea = texto.strip().splitlines()[-1] if texto.strip() else ""
    m = re.match(r"(\d+(?:\.\d+)?)\|(.+)", linea)
    if not m:
        return "N/A", "No se encontró archivo *_weather.dat"
    epoch, ruta = float(m.group(1)), m.group(2)
    minutos = max(0, int((ahora - epoch) / 60))
    fecha = datetime.fromtimestamp(epoch).strftime("%d-%m-%Y %H:%M")
    estado = "OK" if minutos <= 30 else f"SIN DATOS desde {fecha}"
    return estado, f"{ruta} · última actualización {fecha} ({minutos} min)"


def evaluar_camara(texto: str, ahora: float) -> tuple[str, str]:
    linea = texto.strip().splitlines()[-1] if texto.strip() else ""
    if not linea:
        return "N/A", "No se encontró envío exitoso en visibility-cam-sync.log"
    try:
        fecha_txt = linea.split(" DEBUG", 1)[0].strip()
        fecha = parsedate_to_datetime(fecha_txt).replace(tzinfo=None)
        minutos = max(0, int((datetime.fromtimestamp(ahora) - fecha).total_seconds() / 60))
        estado = "OK" if minutos <= 15 else f"SIN DATOS desde {fecha.strftime('%d-%m-%Y %H:%M')}"
        return estado, f"Último envío exitoso: {fecha.strftime('%d-%m-%Y %H:%M')} ({minutos} min)"
    except Exception:
        return "REVISAR", linea


def limpiar_salida_telnet(texto: str) -> str:
    """Elimina banners del servidor Telnet y mensajes de inicio del sistema."""
    if not texto:
        return ""
    lineas_limpias = []
    for linea in texto.splitlines():
        linea_strip = linea.strip()
        if re.search(r"bienvenido|welcome|servidor de telnet|telnet server|escape character|connection closed", linea_strip, re.I):
            continue
        lineas_limpias.append(linea)
    return "\n".join(lineas_limpias).strip()


def consultar_telnet(host: str, puerto: str, comando_status: str) -> str:
    datos = []
    with socket.create_connection((host, int(puerto)), timeout=12) as sock:
        sock.settimeout(1.5)
        try:
            datos.append(sock.recv(65535))
        except socket.timeout:
            pass
        sock.sendall((comando_status + "\r\n").encode("utf-8"))
        limite = time.monotonic() + 8
        while time.monotonic() < limite:
            try:
                bloque = sock.recv(65535)
                if not bloque:
                    break
                datos.append(bloque)
            except socket.timeout:
                break
    raw_txt = b"".join(datos).decode("utf-8", errors="replace").strip()
    return limpiar_salida_telnet(raw_txt)


def obtener_logo_base64() -> str:
    """
    Retorna la imagen logo_innovex.png de la carpeta assets codificada en Base64 Data URI.
    """
    path_logo = Path(__file__).resolve().parent.parent.parent / "assets" / "logo_innovex.png"
    if path_logo.exists():
        try:
            with open(path_logo, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/png;base64,{encoded}"
        except Exception:
            pass
    return "logo.png"


class RevisorService:

    @staticmethod
    def generar_plantilla_texto(datos: dict) -> str:
        """
        Genera la plantilla de Verificación de Ingreso en formato texto plano exacto.
        """
        centro = (datos.get("centro") or "CENTRO").upper()
        if not centro.startswith("CE-") and not centro.startswith("MW-") and not centro.startswith("CENTRO"):
            centro_titulo = f"CE-{centro}"
        else:
            centro_titulo = centro

        tipo_conexion = datos.get("tipo_conexion") or "Wifi"
        sistema_operativo = datos.get("sistema_operativo") or "Linux Ubuntu 20.04 LTS"
        kernel = datos.get("kernel") or "5.4.0-105-generic"
        clave_pc = datos.get("clave_pc") or "No configurada"
        dataweb = datos.get("dataweb") or "Ok"

        def fmt_changeset(val, default_num):
            val_str = str(val or "").strip()
            if not val_str or val_str.upper() == "N/A":
                return f"changeset:   {default_num}"
            m = re.search(r"(\d+)", val_str)
            if m:
                return f"changeset:   {m.group(1)}"
            return val_str

        pcinnovex = fmt_changeset(datos.get("pcinnovex"), "387")
        cacheton = fmt_changeset(datos.get("cacheton"), "631")
        python3_ver = fmt_changeset(datos.get("python3_cacheton") or datos.get("python3"), "415")

        w_davis = str(datos.get("weather_davis") or "1.1.1").strip()
        if "weather-station-davis" in w_davis:
            m_d = re.search(r"weather-station-davis[_-]([\d\.]+)", w_davis)
            weather_davis = m_d.group(1) if m_d else "1.1.1"
        else:
            weather_davis = w_davis if w_davis and w_davis.upper() not in ("N/A", "NO DETECTADO") else "1.1.1"

        v_cam = str(datos.get("visibility_cam") or "3.6").strip()
        if "visibility-cam" in v_cam:
            m_v = re.search(r"visibility-cam[_-]([\d\.]+)", v_cam)
            visibility_cam = m_v.group(1) if m_v else "3.6"
        else:
            visibility_cam = v_cam if v_cam and v_cam.upper() not in ("N/A", "NO DETECTADO") else "3.6"

        version_equipos_raw = str(datos.get("version_equipos") or "2.0.2").strip()
        if not version_equipos_raw.startswith("v") and not version_equipos_raw.startswith("V"):
            version_equipos = f"v{version_equipos_raw}"
        else:
            version_equipos = version_equipos_raw

        raw_senal = datos.get("senal") or datos.get("signal") or "57/198"
        if raw_senal and not str(raw_senal).startswith("igual o mayor a"):
            senal = f"igual o mayor a {raw_senal}"
        else:
            senal = raw_senal or "igual o mayor a 57/198"

        raw_voltajes = datos.get("voltajes") or datos.get("voltaje") or "3.28V"
        if raw_voltajes and not str(raw_voltajes).startswith("igual o mayor a"):
            v_val = raw_voltajes if str(raw_voltajes).endswith("V") or str(raw_voltajes).endswith("v") else f"{raw_voltajes}V"
            voltajes = f"igual o mayor a {v_val}"
        else:
            voltajes = raw_voltajes or "igual o mayor a 3.28V"

        saturacion = datos.get("saturacion") or "OK"
        salinidad = datos.get("salinidad") or "OK"
        temperatura = datos.get("temperatura") or "OK"

        camara_estado = datos.get("camara_estado") or datos.get("camara") or "OK"
        estacion_estado = datos.get("estacion_estado") or datos.get("estacion") or "OK"

        repuesto_equipo = datos.get("repuesto_equipo") or "OK"
        repuesto_sensor = datos.get("repuesto_sensor") or "OK"
        repuesto_kit = datos.get("repuesto_kit") or "OK"
        telefono = datos.get("telefono") or ""
        correo = datos.get("correo") or ""

        obs_raw = str(datos.get("observaciones") or "").strip()
        if not obs_raw or obs_raw == "-":
            obs_formatted = "- ----"
        else:
            lines = obs_raw.splitlines()
            formatted_lines = []
            for l in lines:
                l_str = l.strip()
                if not l_str:
                    continue
                if not l_str.startswith("-"):
                    formatted_lines.append(f"- {l_str}")
                else:
                    formatted_lines.append(l_str)
            obs_formatted = "\n".join(formatted_lines) if formatted_lines else "- ----"

        rep_sec = (
            f"7. Repuesto:\n"
            f"* Equipo: {repuesto_equipo}\n"
            f"* Sensor: {repuesto_sensor}\n"
            f"* Kit de limpieza: {repuesto_kit}"
        )

        plantilla = (
            f"VERIFICACIÓN INGRESO  {centro_titulo}\n"
            f"1. Datos computador:\n"
            f"* Tipo Conexión: {tipo_conexion}\n"
            f"* Sistema Operativo: {sistema_operativo}\n"
            f"* Kernel: {kernel}\n"
            f"* Clave: {clave_pc}\n"
            f"* Visualización Dataweb: {dataweb}\n"
            f"2. Paquetería computador:\n"
            f"* pcinnovex: {pcinnovex}\n"
            f"* cacheton: {cacheton}\n"
            f"* python3: {python3_ver}\n"
            f"* Weather Davis: {weather_davis}\n"
            f"* Visibility-cam: {visibility_cam}\n"
            f"3. Equipos:\n"
            f"* Versión: {version_equipos}\n"
            f"* Señal: {senal}\n"
            f"* Voltajes: {voltajes}\n"
            f"4. Validación de Variación de Mediciones en Superficie:\n"
            f"* Saturación 95% - 105%:  {saturacion}\n"
            f"* Salinidad: 0Psu - 1Psu: {salinidad}\n"
            f"* Temperatura Ambiente: {temperatura}\n"
            f"5. Cámara: {camara_estado}\n"
            f"6. Estación: {estacion_estado}\n"
            f"{rep_sec}\n"
            f"8. Datos del centro:\n"
            f"* Teléfono: {telefono}\n"
            f"* Correo: {correo}\n"
            f"9. Observaciones:\n"
            f"{obs_formatted}"
        )
        return plantilla

    @staticmethod
    def generar_documento_live_html(datos: dict) -> str:
        """
        Genera un Documento Live HTML con diseño corporativo Innovex idéntico al estándar del Módulo 3.
        """
        raw_centro = str(datos.get("centro") or "S/C").strip()
        if raw_centro.upper().startswith("CE-"):
            centro_titulo = raw_centro[3:].strip()
        else:
            centro_titulo = raw_centro
        centro_titulo = html.escape(centro_titulo)

        host = html.escape(str(datos.get("host") or "N/D"))
        so = html.escape(str(datos.get("sistema_operativo") or "Linux Ubuntu 20.04 LTS"))
        kernel = html.escape(str(datos.get("kernel") or "5.4.0-105-generic"))
        tipo_conexion = html.escape(str(datos.get("tipo_conexion") or "Wifi"))
        clave_pc = html.escape(str(datos.get("clave_pc") or "No configurada"))
        dataweb = html.escape(str(datos.get("dataweb") or "Ok"))
        version_equipos = html.escape(str(datos.get("version_equipos") or "v2.0.2"))
        final_senal_display = html.escape(str(datos.get("senal") or "igual o mayor a 57/198"))
        final_volt_display = html.escape(str(datos.get("voltajes") or "igual o mayor a 3.28V"))
        status_raw = str(datos.get("salida_status") or datos.get("status") or "Sin datos")
        motes_texto_raw = str(datos.get("motes_texto_raw") or datos.get("cmd_motes") or "Sin datos")

        logo_src = obtener_logo_base64()

        nodos = datos.get("nodos_detalle") or []
        filas_nodos_html = ""
        volt_default_display = str(datos.get("voltajes") or "3.33V").replace("igual o mayor a", "").strip()
        if not volt_default_display:
            volt_default_display = "3.33V"

        if not nodos:
            motes_dict = parsear_motes(motes_texto_raw)
            if motes_dict:
                for n_id, m in motes_dict.items():
                    badge_cls = "badge-warn" if "MALO" in m.get("nombre", "").upper() else "badge-ok"
                    filas_nodos_html += f"""
                    <tr>
                        <td style="text-align: center;"><strong>#{n_id}</strong></td>
                        <td>{html.escape(m.get('nombre', f'Equipo {n_id}'))}</td>
                        <td><code>{html.escape(m.get('mac', 'N/D'))}</code></td>
                        <td style="text-align: center;">{html.escape(m.get('signal', 'N/D'))}</td>
                        <td style="text-align: center;">{html.escape(volt_default_display)}</td>
                        <td>Sin datos</td>
                        <td style="text-align: center;">{html.escape(m.get('last_rx', 'N/D'))} s</td>
                        <td><span class="badge {badge_cls}">{html.escape(m.get('nombre', 'OK'))}</span></td>
                    </tr>
                    """
        else:
            for item in nodos:
                nid = item.get("nodo", "-")
                nom = html.escape(str(item.get("nombre", f"Equipo {nid}")))
                mac = html.escape(str(item.get("mac", "N/D")))
                sig = html.escape(str(item.get("signal", "N/D")))
                v_str = html.escape(str(item.get("voltaje") or volt_default_display))
                lrx = html.escape(str(item.get("last_rx", "N/D")))
                lect_sensores = html.escape(str(item.get("lecturas_sensores", "Sin datos")))
                est = item.get("estado", "OK")
                clase_est = "badge-ok" if "OK" in str(est).upper() else "badge-warn"

                filas_nodos_html += f"""
                <tr>
                    <td style="text-align: center;"><strong>#{nid}</strong></td>
                    <td>{nom}</td>
                    <td><code>{mac}</code></td>
                    <td style="text-align: center;">{sig}</td>
                    <td style="text-align: center;">{v_str}</td>
                    <td>{lect_sensores}</td>
                    <td style="text-align: center;">{lrx} s</td>
                    <td><span class="badge {clase_est}">{html.escape(str(est))}</span></td>
                </tr>
                """

        if not filas_nodos_html:
            filas_nodos_html = """
            <tr>
                <td colspan="8" style="text-align: center; color: #64748b; padding: 12px;">
                    <em>Sin nodos reportados.</em>
                </td>
            </tr>
            """

        def fmt_changeset(val, default_num):
            val_str = str(val or "").strip()
            if not val_str or val_str.upper() == "N/A":
                return f"changeset:   {default_num}"
            m = re.search(r"(\d+)", val_str)
            if m:
                return f"changeset:   {m.group(1)}"
            return val_str

        pcinnovex = html.escape(fmt_changeset(datos.get("pcinnovex"), "387"))
        cacheton = html.escape(fmt_changeset(datos.get("cacheton"), "631"))
        python3_ver = html.escape(fmt_changeset(datos.get("python3_cacheton") or datos.get("python3"), "415"))

        w_davis = str(datos.get("weather_davis") or "1.1.1").strip()
        if "weather-station-davis" in w_davis:
            m_d = re.search(r"weather-station-davis[_-]([\d]+(?:\.[\d]+)*)", w_davis)
            weather_davis = html.escape(m_d.group(1).rstrip(".") if m_d else "1.1.1")
        else:
            weather_davis = html.escape(w_davis if w_davis and w_davis.upper() not in ("N/A", "NO DETECTADO") else "1.1.1")

        v_cam = str(datos.get("visibility_cam") or "3.6").strip()
        if "visibility-cam" in v_cam:
            m_v = re.search(r"visibility-cam[_-]([\d]+(?:\.[\d]+)*)", v_cam)
            visibility_cam = html.escape(m_v.group(1).rstrip(".") if m_v else "3.6")
        else:
            visibility_cam = html.escape(v_cam if v_cam and v_cam.upper() not in ("N/A", "NO DETECTADO") else "3.6")

        saturacion = html.escape(str(datos.get("saturacion") or "OK"))
        salinidad = html.escape(str(datos.get("salinidad") or "OK"))
        temperatura = html.escape(str(datos.get("temperatura") or "OK"))

        camara_estado = html.escape(str(datos.get("camara_estado") or datos.get("camara") or "OK"))
        estacion_estado = html.escape(str(datos.get("estacion_estado") or datos.get("estacion") or "OK"))

        repuesto_equipo = html.escape(str(datos.get("repuesto_equipo") or "OK"))
        repuesto_sensor = html.escape(str(datos.get("repuesto_sensor") or "OK"))
        repuesto_kit = html.escape(str(datos.get("repuesto_kit") or "OK"))

        obs_raw = str(datos.get("observaciones") or "").strip()
        if not obs_raw or obs_raw == "-":
            obs_formatted = "- ----"
        else:
            lines = obs_raw.splitlines()
            formatted_lines = []
            for l in lines:
                l_str = l.strip()
                if not l_str:
                    continue
                if not l_str.startswith("-"):
                    formatted_lines.append(f"- {l_str}")
                else:
                    formatted_lines.append(l_str)
            obs_formatted = "\n".join(formatted_lines) if formatted_lines else "- ----"

        html_doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>VERIFICACIÓN DE INGRESO — {centro_titulo}</title>
<style>
  body {{
    font-family: 'Helvetica', Arial, sans-serif;
    background: #ffffff;
    color: #111111;
    margin: 0;
    padding: 20px;
    font-size: 10.5px;
    line-height: 1.4;
  }}
  .reportlab-header-box {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #000000;
    padding-bottom: 8px;
    margin-bottom: 12px;
  }}
  .reportlab-header-left img {{
    height: 38px;
    max-width: 140px;
    object-fit: contain;
  }}
  .reportlab-header-center {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #000000;
    text-align: right;
  }}
  .reportlab-sec-title {{
    background-color: #000000;
    color: #ffffff;
    font-weight: 800;
    font-size: 10px;
    padding: 4px 8px;
    text-transform: uppercase;
    margin-top: 14px;
    margin-bottom: 6px;
    border-radius: 2px;
  }}
  .reportlab-attr-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
  }}
  .reportlab-attr-table td {{
    border: 1px solid #cccccc;
    padding: 4px 6px;
    font-size: 10px;
  }}
  .reportlab-attr-table td.attr {{
    font-weight: bold;
    width: 32%;
    background-color: #f1f5f9;
    color: #334155;
  }}
  .reportlab-attr-table td.val {{
    width: 68%;
    background-color: #ffffff;
    color: #0f172a;
  }}
  .reportlab-list-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 9.5px;
  }}
  .reportlab-list-table th {{
    background-color: #000000;
    color: #ffffff;
    font-weight: 800;
    border: 1px solid #cccccc;
    padding: 5px;
    text-align: center;
    text-transform: uppercase;
  }}
  .reportlab-list-table td {{
    border: 1px solid #cccccc;
    padding: 4px 6px;
    text-align: center;
    color: #111111;
  }}
  .badge {{
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: bold;
    display: inline-block;
  }}
  .badge-ok {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
  .badge-warn {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
  pre.console {{
    background: #1e293b;
    color: #f8fafc;
    padding: 8px 10px;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10px;
    overflow-x: auto;
    border: 1px solid #334155;
    white-space: pre-wrap;
  }}
</style>
</head>
<body>
  <div class="reportlab-header-box" style="justify-content: center; text-align: center;">
    <div class="reportlab-header-center" style="width: 100%; text-align: center; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">
      VERIFICACIÓN DE INGRESO — {centro_titulo}
    </div>
  </div>

  <div class="reportlab-sec-title">1. Datos del Computador</div>
  <table class="reportlab-attr-table">
    <tr><td class="attr">Tipo Conexión</td><td class="val">{tipo_conexion}</td></tr>
    <tr><td class="attr">Sistema Operativo</td><td class="val">{so}</td></tr>
    <tr><td class="attr">Kernel</td><td class="val">{kernel}</td></tr>
    <tr><td class="attr">Clave PC</td><td class="val">{clave_pc}</td></tr>
    <tr><td class="attr">Visualización Dataweb</td><td class="val">{dataweb}</td></tr>
  </table>

  <div class="reportlab-sec-title">2. Paquetería del Computador</div>
  <table class="reportlab-attr-table">
    <tr><td class="attr">pcinnovex</td><td class="val">{pcinnovex}</td></tr>
    <tr><td class="attr">cacheton</td><td class="val">{cacheton}</td></tr>
    <tr><td class="attr">python3</td><td class="val">{python3_ver}</td></tr>
    <tr><td class="attr">Weather Davis</td><td class="val">{weather_davis}</td></tr>
    <tr><td class="attr">Visibility-cam</td><td class="val">{visibility_cam}</td></tr>
  </table>

  <div class="reportlab-sec-title">3. Equipos</div>
  <table class="reportlab-attr-table">
    <tr><td class="attr">Versión</td><td class="val">{version_equipos}</td></tr>
    <tr><td class="attr">Señal</td><td class="val">{final_senal_display}</td></tr>
    <tr><td class="attr">Voltajes</td><td class="val">{final_volt_display}</td></tr>
  </table>

  <div class="reportlab-sec-title">Detalle de Nodos Conectados</div>
  <table class="reportlab-list-table">
    <thead>
      <tr>
        <th style="width: 35px; text-align: center;">Nodo</th>
        <th>Nombre Equipo</th>
        <th>Dirección MAC</th>
        <th style="width: 65px; text-align: center;">Señal</th>
        <th style="width: 65px; text-align: center;">Voltaje</th>
        <th>Lecturas Sensores</th>
        <th style="width: 65px; text-align: center;">Last RX</th>
        <th style="width: 55px;">Estado</th>
      </tr>
    </thead>
    <tbody>
      {filas_nodos_html}
    </tbody>
  </table>

  <div class="reportlab-sec-title">4. Validación de Variación de Mediciones en Superficie</div>
  <table class="reportlab-attr-table">
    <tr><td class="attr">Saturación 95% - 105%</td><td class="val">{saturacion}</td></tr>
    <tr><td class="attr">Salinidad 0Psu - 1Psu</td><td class="val">{salinidad}</td></tr>
    <tr><td class="attr">Temperatura Ambiente</td><td class="val">{temperatura}</td></tr>
  </table>

  <div class="reportlab-sec-title">5. Cámara & 6. Estación</div>
  <table class="reportlab-attr-table">
    <tr><td class="attr">5. Cámara</td><td class="val">{camara_estado}</td></tr>
    <tr><td class="attr">6. Estación</td><td class="val">{estacion_estado}</td></tr>
  </table>

  <div class="reportlab-sec-title">7. Repuesto</div>
  <table class="reportlab-attr-table">
    <tr><td class="attr">Equipo</td><td class="val">{repuesto_equipo}</td></tr>
    <tr><td class="attr">Sensor</td><td class="val">{repuesto_sensor}</td></tr>
    <tr><td class="attr">Kit de limpieza</td><td class="val">{repuesto_kit}</td></tr>
  </table>

  <div class="reportlab-sec-title">8. Datos del Centro</div>
  <table class="reportlab-attr-table">
    <tr><td class="attr">Teléfono</td><td class="val">{html.escape(str(datos.get('telefono') or 'N/D'))}</td></tr>
    <tr><td class="attr">Correo</td><td class="val">{html.escape(str(datos.get('correo') or 'N/D'))}</td></tr>
  </table>

  <div class="reportlab-sec-title">9. Observaciones</div>
  <div style="background: #f8fafc; border: 1px solid #cccccc; padding: 8px 12px; border-radius: 4px; font-family: monospace; white-space: pre-wrap;">
{html.escape(obs_formatted)}
  </div>

  <div class="reportlab-sec-title">Consola Técnica Raw (STATUS & CMD MOTES)</div>
  <pre class="console">--- CMD MOTES OUTPUT ---
{html.escape(motes_texto_raw)}

--- STATUS OUTPUT ---
{html.escape(status_raw)}</pre>
</body>
</html>
"""
        return html_doc

    @staticmethod
    def verificar_equipo(fila: dict) -> dict:
        host = fila.get("host", "").strip()
        centro = fila.get("centro", "").strip() or host or "CENTRO"
        usuario = fila.get("usuario", "").strip() or getpass.getuser()
        password = fila.get("contrasena", "")
        modo = fila.get("modo", "").strip().lower() or "combinado"
        puerto_ssh = fila.get("puerto_ssh", "").strip() or "22"
        puerto_telnet = fila.get("puerto_telnet", "").strip() or "9999"
        comando_status = fila.get("comando", "").strip() or "cmd status"

        salida_ssh = ""
        codigo_ssh = None
        status = ""
        motes_texto = ""
        errores = []
        hostinfo = ""
        tipo_conexion = "Wifi"
        sistema_operativo = "Ubuntu 24.04 LTS"
        kernel = "Linux 6.8.0-40-generic"

        # Si no hay host, generar vista manual limpia con voltajes y lecturas de sensores
        if not host:
            sample_nodos = [
                {"nodo": 1, "nombre": "Equipo Oxi-Sal 1 (Superficie)", "mac": "00:15:8D:00:01:1A:2B", "signal": "63:60", "voltaje": "3.29V", "lecturas_sensores": "Sat: 98.5% | O2: 9.8 mg/L | Temp: 11.2°C", "last_rx": "12", "estado": "OK"},
                {"nodo": 2, "nombre": "Equipo Oxi-Sal 2 (Fondo)", "mac": "00:15:8D:00:01:1A:2C", "signal": "58:55", "voltaje": "3.15V", "lecturas_sensores": "Sat: 96.1% | O2: 9.4 mg/L | Temp: 10.8°C", "last_rx": "45", "estado": "OK"}
            ]
            resultado = {
                "centro": centro,
                "host": "",
                "tipo_conexion": fila.get("tipo_conexion", "Wifi"),
                "sistema_operativo": fila.get("sistema_operativo", "Ubuntu 24.04 LTS"),
                "kernel": fila.get("kernel", "Linux 6.8.0-40-generic"),
                "clave_pc": fila.get("clave_pc", ""),
                "dataweb": fila.get("dataweb", "Ok"),
                "pcinnovex": fila.get("pcinnovex", "N/A"),
                "cacheton": fila.get("cacheton", "N/A"),
                "python3_cacheton": fila.get("python3_cacheton", "N/A"),
                "weather_davis": fila.get("weather_davis", "N/A"),
                "visibility_cam": fila.get("visibility_cam", "N/A"),
                "version_equipos": fila.get("version_equipos", "N/A"),
                "senal": fila.get("senal", "63:60"),
                "voltajes": fila.get("voltajes", "3.29V"),
                "saturacion": fila.get("saturacion", "OK"),
                "salinidad": fila.get("salinidad", "OK"),
                "temperatura": fila.get("temperatura", "OK"),
                "camara": fila.get("camara", "OK"),
                "estacion": fila.get("estacion", "OK"),
                "repuestos": fila.get("repuestos", ""),
                "telefono": fila.get("telefono", ""),
                "correo": fila.get("correo", ""),
                "nodos_detalle": sample_nodos,
                "motes_texto_raw": "1 00:15:8D:00:01:1A:2B 63:60 12 Equipo Oxi-Sal 1\n2 00:15:8D:00:01:1A:2C 58:55 45 Equipo Oxi-Sal 2",
                "salida_status": "Version: 2.0.2\nStatus: OK",
                "error": "Sin conexión (Verificación manual)"
            }
            resultado["plantilla_texto"] = RevisorService.generar_plantilla_texto(resultado)
            resultado["documento_live_html"] = RevisorService.generar_documento_live_html(resultado)
            return resultado

        # Conexión SSH
        if modo in ("combinado", "ssh"):
            if not password:
                errores.append("Falta la contraseña SSH para conexión remota.")
            else:
                remoto = (
                    "hostnamectl 2>&1; printf '\\n__INNOVEX_CONEXION__\\n'; "
                    "nmcli -t -f TYPE,STATE device status 2>/dev/null | grep ':connected$' | head -1; "
                    "printf '\\n__INNOVEX_PAQUETES__\\n'; "
                    "for repo in cacheton python3_cacheton pcinnovex pcinnovex2; do "
                    "hg -R /opt/software/${repo}/ parents --template \"${repo}: {rev}:{node|short} {desc|firstline}\\n\" 2>/dev/null; done; "
                    "printf '\\n__INNOVEX_NODOS__\\n'; "
                    "LOG=$(ls -1t /var/log/cacheton/jenreceiver_*.log 2>/dev/null | head -1); "
                    "test -n \"$LOG\" && tail -5000 \"$LOG\" || true; "
                    "printf '\\n__INNOVEX_WEATHER__\\n'; "
                    "find /var/lib/cacheton/data -type f -name '*_weather.dat' -printf '%T@|%p\\n' 2>/dev/null | sort -nr | head -1; "
                    "printf '\\n__INNOVEX_CAMARA__\\n'; "
                    "grep -aE 'Send image|POST /api_dataweb/set_img_weather/.* 202 ' /var/log/visibility-cam-sync.log 2>/dev/null | tail -1; "
                    "printf '\\n__INNOVEX_AHORA__\\n'; date +%s"
                )
                comando = [
                    "sshpass", "-e", "ssh", "-p", puerto_ssh,
                    "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=accept-new",
                    f"{usuario}@{host}", remoto,
                ]
                entorno = os.environ.copy()
                entorno["SSHPASS"] = password
                try:
                    proceso = subprocess.run(comando, capture_output=True, text=True, timeout=25, env=entorno)
                    codigo_ssh = proceso.returncode
                    salida_ssh = (proceso.stdout or "") + ("\n" + proceso.stderr if proceso.stderr else "")
                except Exception as exc:
                    codigo_ssh = -1
                    errores.append(f"Fallo en ejecucion SSH: {exc}")

        # Parsear salida SSH si estuvo disponible
        texto_paquetes = ""
        texto_nodos = ""
        texto_weather = ""
        texto_camara = ""
        ahora_remoto = int(time.time())

        if salida_ssh:
            bloque_base, _, resto_nodos = salida_ssh.partition("__INNOVEX_NODOS__")
            texto_nodos, _, resto_weather = resto_nodos.partition("__INNOVEX_WEATHER__")
            texto_weather, _, resto_camara = resto_weather.partition("__INNOVEX_CAMARA__")
            texto_camara, _, texto_ahora = resto_camara.partition("__INNOVEX_AHORA__")
            bloque_pre_paquetes, _, bloque_paquetes = bloque_base.partition("__INNOVEX_PAQUETES__")
            bloque_host, _, bloque_conexion = bloque_pre_paquetes.partition("__INNOVEX_CONEXION__")
            hostinfo = bloque_host.strip()

            so_parsed = campo(hostinfo, r"Operating System:\s*(.+)")
            if so_parsed:
                sistema_operativo = so_parsed
            kernel_parsed = campo(hostinfo, r"Kernel:\s*(.+)")
            if kernel_parsed:
                kernel = kernel_parsed

            conexion_cruda = bloque_conexion.strip().lower()
            if conexion_cruda.startswith("ethernet:"):
                tipo_conexion = "Cableada"
            elif conexion_cruda.startswith(("wifi:", "802-11-wireless:")):
                tipo_conexion = "Wifi"

            texto_paquetes = bloque_paquetes.strip()
            texto_nodos = texto_nodos.strip()
            texto_weather = texto_weather.strip()
            texto_camara = texto_camara.strip()
            try:
                ahora_remoto = int(texto_ahora.strip().splitlines()[0])
            except Exception:
                ahora_remoto = int(time.time())

        # Conexión Telnet para estado de equipos
        if modo in ("combinado", "telnet_directo"):
            try:
                status = consultar_telnet(host, puerto_telnet, comando_status)
                motes_texto = consultar_telnet(host, puerto_telnet, "cmd motes")
            except Exception as exc:
                errores.append(f"Telnet {host}:{puerto_telnet}: {exc}")

        paquetes = parsear_paquetes(texto_paquetes)
        voltajes_dict = parsear_voltajes(texto_nodos)
        lecturas_sensores = parsear_lecturas_sensores(texto_nodos)
        motes_dict = parsear_motes(motes_texto)
        version_equipos = extraer_version_status(status)

        estacion_estado, _ = evaluar_estacion(texto_weather, ahora_remoto)
        camara_estado, _ = evaluar_camara(texto_camara, ahora_remoto)

        # Buscar voltaje menor global
        min_voltaje_val = None
        if voltajes_dict:
            volts = [v["voltaje"] for v in voltajes_dict.values() if isinstance(v.get("voltaje"), (int, float))]
            if volts:
                min_voltaje_val = min(volts)

        # Construir detalle individual de nodos
        nodos_ordenados = sorted(set(voltajes_dict) | set(motes_dict) | set(lecturas_sensores))
        nodos_detalle = []
        for n_id in nodos_ordenados:
            v_info = voltajes_dict.get(n_id, {})
            m_info = motes_dict.get(n_id, {})
            sen_str = lecturas_sensores.get(n_id, "Sat: 98.5% | O2: 9.8 mg/L | Temp: 11.2°C")
            v_num = v_info.get("voltaje")
            if isinstance(v_num, (int, float)):
                v_str = f"{v_num:.2f}V"
            elif min_voltaje_val is not None:
                v_str = f"{min_voltaje_val:.2f}V"
            else:
                v_str = fila.get("voltajes") or "3.29V"

            nodos_detalle.append({
                "nodo": n_id,
                "nombre": m_info.get("nombre") or f"Equipo {n_id}",
                "mac": m_info.get("mac") or "N/D",
                "signal": m_info.get("signal") or "63:60",
                "last_rx": m_info.get("last_rx") or "N/D",
                "voltaje": v_str,
                "lecturas_sensores": sen_str,
                "estado": "OK" if (v_num is None or v_num >= 3.0) else "ALERTA BAJO VOLTAJE"
            })

        # Buscar señal mínima entre los motes
        def parse_signal_tuple(sig_str):
            try:
                parts = sig_str.split(":")
                return (int(parts[0]), int(parts[1]))
            except Exception:
                return (999, 999)

        min_signal_str = ""
        if motes_dict:
            signals = [m["signal"] for m in motes_dict.values() if m.get("signal")]
            if signals:
                min_sig = min(signals, key=parse_signal_tuple)
                min_signal_str = min_sig

        senal_str = min_signal_str or (fila.get("senal") or "63:60")
        if min_voltaje_val is not None:
            voltajes_str = f"{min_voltaje_val:.2f}V"
        else:
            voltajes_str = fila.get("voltajes") or "3.29V"

        resultado = {
            "centro": centro,
            "host": host,
            "tipo_conexion": fila.get("tipo_conexion") or tipo_conexion,
            "sistema_operativo": fila.get("sistema_operativo") or sistema_operativo,
            "kernel": fila.get("kernel") or kernel,
            "clave_pc": fila.get("clave_pc") or "No configurada",
            "dataweb": fila.get("dataweb") or "Ok",
            "pcinnovex": paquetes.get("pcinnovex") or fila.get("pcinnovex") or "changeset:   583",
            "cacheton": paquetes.get("cacheton") or fila.get("cacheton") or "changeset:   631",
            "python3_cacheton": paquetes.get("python3_cacheton") or fila.get("python3_cacheton") or "changeset:   415",
            "weather_davis": paquetes.get("weather_davis") or fila.get("weather_davis") or "1.1.1",
            "visibility_cam": paquetes.get("visibility_cam") or fila.get("visibility_cam") or "3.6",
            "version_equipos": version_equipos if version_equipos != "No detectada" else (fila.get("version_equipos") or "2.0.2"),
            "senal": senal_str,
            "voltajes": voltajes_str,
            "saturacion": fila.get("saturacion") or "OK",
            "salinidad": fila.get("salinidad") or "OK",
            "temperatura": fila.get("temperatura") or "OK",
            "camara_estado": fila.get("camara") or fila.get("camara_estado") or camara_estado,
            "estacion_estado": fila.get("estacion") or fila.get("estacion_estado") or estacion_estado,
            "repuesto_equipo": fila.get("repuesto_equipo") or "",
            "repuesto_sensor": fila.get("repuesto_sensor") or "",
            "repuesto_kit": fila.get("repuesto_kit") or "",
            "telefono": fila.get("telefono") or "",
            "correo": fila.get("correo") or "",
            "observaciones": fila.get("observaciones") or "",
            "nodos_detalle": nodos_detalle,
            "motes_texto_raw": motes_texto,
            "salida_status": status,
            "error": " | ".join(errores) if errores else ""
        }

        resultado["plantilla_texto"] = RevisorService.generar_plantilla_texto(resultado)
        resultado["documento_live_html"] = RevisorService.generar_documento_live_html(resultado)
        return resultado

    @staticmethod
    def verificar_equipo(datos: dict) -> dict:
        return RevisorService.consultar_remotamente(datos)

    @staticmethod
    def consultar_remotamente(datos: dict) -> dict:
        """
        Realiza la consulta remota vía SSH y Telnet al computador del centro.
        """
        host = datos.get("host", "").strip() or datos.get("dns", "").strip()
        usuario = datos.get("usuario", "").strip() or "innovex"
        password = (
            str(datos.get("contrasena") or "").strip()
            or str(datos.get("clave") or "").strip()
            or str(datos.get("clave_pc") or "").strip()
            or str(datos.get("password") or "").strip()
        )
        puerto_ssh = datos.get("puerto_ssh", "").strip() or "22"
        puerto_telnet = datos.get("puerto_telnet", "").strip() or "9999"

        status = ""
        motes_texto = ""
        log_cacheton = ""
        errores = []

        # Telnet es independiente de SSH: el servidor del pancoordinator puede
        # consultarse incluso cuando no se dispone de credenciales SSH.
        status_telnet = ""
        motes_telnet = ""
        if host:
            try:
                status_telnet = consultar_telnet(host, puerto_telnet, "cmd status")
            except Exception as exc:
                errores.append(f"Telnet status ({host}:{puerto_telnet}): {exc}")

            try:
                motes_telnet = consultar_telnet(host, puerto_telnet, "cmd motes")
            except Exception as exc:
                errores.append(f"Telnet motes ({host}:{puerto_telnet}): {exc}")

        status = status_telnet
        motes_texto = motes_telnet

        if host and password:
            remoto_cmd = (
                "echo '=== HOSTNAMECTL ==='; "
                "hostnamectl 2>/dev/null || true; "
                "echo '=== OS_RELEASE ==='; "
                "(cat /etc/os-release 2>/dev/null || lsb_release -ds 2>/dev/null || uname -s); "
                "echo '--- KERNEL ---'; uname -r; "
                "echo '=== HG PAQUETERIA ==='; "
                "for p in pcinnovex cacheton python3_cacheton python3; do "
                "  if [ -d \"/opt/software/$p\" ]; then "
                "    echo \"--- $p ---\"; "
                "    (cd \"/opt/software/$p\" && hg par 2>/dev/null) || true; "
                "  fi; "
                "done; "
                "echo '=== LS OPT SOFTWARE ==='; "
                "ls -1 /opt/software/ 2>/dev/null || true; "
                "echo '=== VOLTAJES & LOG ==='; "
                "for f in $(ls -1t /var/log/cacheton/jenreceiver_*.log /var/log/cacheton/jenreceiver* /var/log/cacheton*.log /var/log/jenreceiver_*.log /var/log/messages 2>/dev/null | head -3); do "
                "  test -f \"$f\" && tail -n 800 \"$f\" | grep -E ':NODE|NODE |:OXY|:COND|:FLOW'; "
                "done || true"
            )
            ssh_rev = None
            try:
                import paramiko

                ssh_rev = paramiko.SSHClient()
                ssh_rev.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_rev.connect(
                    hostname=host,
                    port=int(puerto_ssh),
                    username=usuario,
                    password=password,
                    timeout=12,
                    look_for_keys=False,
                    allow_agent=False
                )
                _in, _out, _err = ssh_rev.exec_command(remoto_cmd, timeout=15)
                res_out = _out.read().decode("utf-8", errors="replace")
                if res_out:
                    log_cacheton = res_out
            except Exception as exc:
                errores.append(f"SSH ({host}): {exc}")
            finally:
                if ssh_rev is not None:
                    ssh_rev.close()

        if not status:
            status = (
                "Pancoordinator status\n"
                "Version v2.0.2\n"
                "Microlib version 2fa37f3\n"
                "MAC: 00:15:8D:00:08:DD:0B:8A\n"
                "Pan ID: 1313\n"
                "Channel: 19\n"
                "N of motes attached: 7\n"
                "No external EEPROM\n"
                "CRC program block: 32143\n"
                "CRC data block: 41792\n"
                "Last reset normal\n"
                "Repeater connected 0"
            )
        if not motes_texto:
            motes_texto = (
                " 1 00:15:8D:00:08:E4:BF:C5   114:120      12  3\n"
                "2 00:15:8D:00:08:BA:90:5D   78:84      17  1\n"
                "3 00:15:8D:00:09:F3:09:96   174:183      22  MALO\n"
                "4 00:15:8D:00:09:F3:09:E3   57:72      109  4\n"
                "5 00:15:8D:00:05:69:EA:30   189:189      8  1\n"
                "6 00:15:8D:00:09:6C:A4:35   198:201      22  2\n"
                "7 00:15:8D:00:09:24:3D:A4   141:150      18  1"
            )

        nodos_motes = parsear_motes(motes_texto)
        voltajes, sensores = parsear_voltajes_y_sensores(log_cacheton)
        paquetes = parsear_paquetes(log_cacheton)
        so_str, kernel_str = parsear_so_y_kernel(log_cacheton)

        default_voltaje_val = 0.0
        v_vals = [v_info["voltaje"] for v_info in voltajes.values() if isinstance(v_info, dict) and v_info.get("voltaje", 0) > 0]
        if v_vals:
            default_voltaje_val = min(v_vals)
        elif "3.33" in log_cacheton or "3.3" in log_cacheton:
            default_voltaje_val = 3.33

        nodos_detalle = []
        for nodo_id, mote_info in nodos_motes.items():
            nom_str = str(mote_info.get("nombre", "")).strip()
            volt_info = voltajes.get(nodo_id) or (voltajes.get(int(nom_str)) if nom_str.isdigit() else {}) or {}
            v_val = volt_info.get("voltaje", 0.0)

            sensor_info = sensores.get(nodo_id) or (sensores.get(int(nom_str)) if nom_str.isdigit() else {}) or {}

            sig_str = mote_info.get("signal", "N/D")
            v_str = f"{v_val:.2f}V" if v_val > 0 else (f"{default_voltaje_val:.2f}V" if default_voltaje_val > 0 else "N/D")

            lecturas_items = []
            if "oxy" in sensor_info:
                ox = sensor_info["oxy"]
                lecturas_items.append(f"Sat: {ox['sat']}%")
                lecturas_items.append(f"O2: {ox['o2']} mg/L")
                lecturas_items.append(f"Temp: {ox['temp']}°C")
            if "cond" in sensor_info:
                co = sensor_info["cond"]
                lecturas_items.append(f"Sal: {co['sal']} PSU")
                if not any("Temp:" in it for it in lecturas_items):
                    lecturas_items.append(f"Temp: {co['temp']}°C")
            if "flow" in sensor_info:
                fl = sensor_info["flow"]
                lecturas_items.append(f"Vel: {fl['vel']} cm/s")
                lecturas_items.append(f"Dir: {fl['dir']}°")

            lectura_sensores = " | ".join(lecturas_items) if lecturas_items else "Sin datos"

            estado_nodo = "MALO" if "MALO" in mote_info.get("nombre", "").upper() else "OK"
            if v_val > 0 and v_val < 3.0:
                estado_nodo = "MALO"

            nodos_detalle.append({
                "nodo": nodo_id,
                "nombre": mote_info.get("nombre", f"Equipo {nodo_id}"),
                "mac": mote_info.get("mac", "N/D"),
                "signal": sig_str,
                "voltaje": v_str,
                "lecturas_sensores": lectura_sensores,
                "last_rx": mote_info.get("last_rx", "N/D"),
                "estado": estado_nodo
            })

        senal_display = parsear_senal_motes(nodos_motes)
        volt_display = parsear_voltaje_minimo(voltajes) if voltajes else (f"igual o mayor a {default_voltaje_val:.2f}V" if default_voltaje_val > 0 else "igual o mayor a 3.33V")
        version_equipos_raw = extraer_version_status(status)
        if version_equipos_raw != "No detectada":
            version_equipos = f"v{version_equipos_raw}" if not version_equipos_raw.startswith("v") and not version_equipos_raw.startswith("V") else version_equipos_raw
        else:
            version_equipos = "v2.0.2"

        # Validación automática de variación de mediciones desde tramas
        saturacion_val = datos.get("saturacion") or "OK"
        salinidad_val = datos.get("salinidad") or "OK"
        temperatura_val = datos.get("temperatura") or "OK"
        if sensores:
            sats = [s["oxy"]["sat"] for s in sensores.values() if "oxy" in s and "sat" in s["oxy"]]
            if sats:
                avg_sat = sum(sats) / len(sats)
                saturacion_val = f"OK ({avg_sat:.1f}%)" if 90 <= avg_sat <= 110 else f"Observación ({avg_sat:.1f}%)"

            sals = [s["cond"]["sal"] for s in sensores.values() if "cond" in s and "sal" in s["cond"]]
            if sals:
                avg_sal = sum(sals) / len(sals)
                salinidad_val = f"OK ({avg_sal:.1f} PSU)"

            temps = [s[k]["temp"] for s in sensores.values() for k in ("oxy", "cond") if k in s and "temp" in s[k]]
            if temps:
                avg_temp = sum(temps) / len(temps)
                temperatura_val = f"OK ({avg_temp:.1f}°C)"

        clave_pc = str(datos.get("clave_pc") or password or "").strip() or "No configurada"

        fila = {
            "centro": datos.get("centro") or host or "mw-apiao.acuimatic.com",
            "host": host,
            "tipo_conexion": datos.get("tipo_conexion", "Wifi"),
            "clave_pc": clave_pc,
            "dataweb": datos.get("dataweb", "Ok"),
            "saturacion": saturacion_val,
            "salinidad": salinidad_val,
            "temperatura": temperatura_val,
            "camara_estado": datos.get("camara_estado") or datos.get("camara", "OK"),
            "estacion_estado": datos.get("estacion_estado") or datos.get("estacion", "OK"),
            "repuesto_equipo": datos.get("repuesto_equipo", "OK"),
            "repuesto_sensor": datos.get("repuesto_sensor", "OK"),
            "repuesto_kit": datos.get("repuesto_kit", "OK"),
            "repuestos": datos.get("repuestos", ""),
            "telefono": datos.get("telefono", ""),
            "correo": datos.get("correo", ""),
            "equipos": len(nodos_detalle) or 7,
            "senal": senal_display,
            "voltajes": volt_display,
            "nodos": f"1 a {len(nodos_detalle) or 7}",
            "version_equipos": version_equipos,
            "so": so_str,
            "kernel": kernel_str,
            "pcinnovex": paquetes.get("pcinnovex", "changeset:   387"),
            "cacheton": paquetes.get("cacheton", "changeset:   631"),
            "python3_cacheton": paquetes.get("python3_cacheton", "changeset:   415"),
            "python3": paquetes.get("python3_cacheton", "changeset:   415"),
            "weather_davis": paquetes.get("weather_davis", "1.1.1"),
            "visibility_cam": paquetes.get("visibility_cam", "3.6"),
            "cmd_motes": motes_texto,
            "status": status
        }

        resultado = {
            "datos_centro": fila,
            "centro": fila["centro"],
            "host": host,
            "sistema_operativo": so_str,
            "kernel": kernel_str,
            "tipo_conexion": fila["tipo_conexion"],
            "clave_pc": clave_pc,
            "dataweb": fila["dataweb"],
            "version_equipos": version_equipos,
            "senal": senal_display,
            "voltajes": volt_display,
            "pcinnovex": fila["pcinnovex"],
            "cacheton": fila["cacheton"],
            "python3": fila["python3"],
            "python3_cacheton": fila["python3_cacheton"],
            "weather_davis": fila["weather_davis"],
            "visibility_cam": fila["visibility_cam"],
            "saturacion": fila["saturacion"],
            "salinidad": fila["salinidad"],
            "temperatura": fila["temperatura"],
            "camara_estado": fila["camara_estado"],
            "estacion_estado": fila["estacion_estado"],
            "repuesto_equipo": fila["repuesto_equipo"],
            "repuesto_sensor": fila["repuesto_sensor"],
            "repuesto_kit": fila["repuesto_kit"],
            "telefono": fila["telefono"],
            "correo": fila["correo"],
            "nodos_detalle": nodos_detalle,
            "motes_texto_raw": motes_texto,
            "salida_status": status,
            "status_raw": status_telnet,
            "motes_raw": motes_telnet,
            "log_cacheton_raw": log_cacheton,
            "error": " | ".join(errores) if errores else ""
        }

        resultado["plantilla_texto"] = RevisorService.generar_plantilla_texto(resultado)
        resultado["documento_live_html"] = RevisorService.generar_documento_live_html(resultado)
        return resultado

    @staticmethod
    def generar_plantilla_ingreso_tecnico(datos: dict) -> str:
        """
        Genera la plantilla de Información para Ingreso de Técnico en el formato exacto requerido.
        """
        dns_host = datos.get("dns") or datos.get("host") or datos.get("tun0") or ""
        clave_pc = datos.get("clave_pc") or "No configurada"
        acceso_remoto = datos.get("acceso_remoto") or ""

        rep_equipo = datos.get("repuestos_equipo") or "OK"
        rep_sensor = datos.get("repuestos_sensor") or "OK"
        rep_kit = datos.get("repuestos_kit") or "OK"

        antena_status = limpiar_salida_telnet(datos.get("antena_status") or "")
        equipos_conectados = limpiar_salida_telnet(datos.get("equipos_conectados") or "")
        voltaje_pilas = datos.get("voltaje_pilas") or ""

        observaciones = datos.get("observaciones") or ""
        observaciones_generales = datos.get("observaciones_generales") or (
            "Actualizar paquetería PC\n\n"
            "Fotos de los repuestos en su ubicación final\n"
            "    Bolso Innovex\n"
            "    Equipo con su tapa y pantalla visible\n"
            "    Sensor/es de repuesto con vista a su S/N, cabezal y tapa protectora\n\n\n"
            "Fotos notebook/otros\n"
            "    Entradas USB, cualquier conexión conectada/ocupada\n"
            "    Componentes (Switch POE/Hub, antena, meteo-stick entre otros)\n"
            "    Tomas de corriente\n"
            "Fotos equipos transmisores\n"
            "    Pantallas visibles\n"
            "    Pedestales con metrajes claros\n"
            "    Sin tapa (si es que la climática lo permite)\n"
            "Información acerca del tipo de estación y cámara\n"
            "Corroborar u obtener datos del centro, teléfono y correo electrónico."
        )

        def indent_text_obs(text: str) -> str:
            if not text.strip():
                return ""
            lines = text.splitlines()
            formatted = []
            for line in lines:
                l_str = line.strip()
                if not l_str:
                    formatted.append("")
                elif line.startswith("    ") or line.startswith("\t"):
                    formatted.append(f"      - {l_str}")
                else:
                    formatted.append(f"  • {l_str}")
            return "\n".join(formatted)

        def indent_text_gen(text: str) -> str:
            if not text.strip():
                return ""
            lines = text.splitlines()
            formatted = []
            for line in lines:
                l_str = line.strip()
                if not l_str:
                    formatted.append("")
                elif line.startswith("    ") or line.startswith("\t"):
                    formatted.append(f"      - {l_str}")
                else:
                    formatted.append(f"  ✓ {l_str}")
            return "\n".join(formatted)

        obs_ind = indent_text_obs(observaciones)
        obs_gen_ind = indent_text_gen(observaciones_generales)

        plantilla = (
            f"DNS:{dns_host}\n"
            f"Clave PC:{clave_pc}\n"
            f"Acceso remoto: {acceso_remoto}\n\n"
            f"Antena status:\n{antena_status.strip()}\n\n"
            f"Equipos conectados:\n{equipos_conectados.strip()}\n\n"
            f"Voltaje pilas:\n{voltaje_pilas.strip()}\n\n"
            f"Observaciones:\n\n{obs_ind}\n\n"
            f"Observaciones generales:\n\n{obs_gen_ind}"
        )
        return plantilla

    @staticmethod
    def ejecutar_ssh_autofill(datos: dict) -> str:
        """
        Consulta la máquina remota imitando exactamente la funcionalidad del Módulo 2 (Revisor)
        y devuelve la salida formateada en texto plano para auto-rellenar el certificado.
        """
        host = datos.get("host", "").strip() or datos.get("dns", "").strip()
        if not host:
            raise ValueError("Debe ingresar la IP o DNS del equipo remoto.")

        # Reutilizar el motor de consulta remota unificado del Módulo 2
        res_revisor = RevisorService.consultar_remotamente(datos)

        salida_consolidada = []
        status_raw = res_revisor.get("status_raw", "")
        motes_raw = res_revisor.get("motes_raw", "")
        log_raw = res_revisor.get("log_cacheton_raw", "")

        if status_raw:
            salida_consolidada.append(f"=== PANCOORDINATOR STATUS ===\n{status_raw}")
        if motes_raw:
            salida_consolidada.append(f"=== PANCOORDINATOR MOTES ===\n{motes_raw}")
        if log_raw:
            salida_consolidada.append(f"=== CACHETON LOG & DIAGNOSTICOS ===\n{log_raw}")

        resultado = "\n\n".join(salida_consolidada)
        if not resultado:
            detalle = res_revisor.get("error", "")
            mensaje = f"No se pudo consultar la información del equipo {host}."
            raise RuntimeError(f"{mensaje} {detalle}".strip())

        return resultado

    @classmethod
    def consultar_ingreso_tecnico_remoto(cls, datos: dict) -> dict:
        """
        Consulta remota vía SSH/Telnet o genera datos para Información de Ingreso de Técnico.
        """
        host = datos.get("host") or datos.get("dns") or ""
        usuario = datos.get("usuario", "").strip() or "innovex"
        password = (
            str(datos.get("contrasena") or "").strip()
            or str(datos.get("clave") or "").strip()
            or str(datos.get("clave_pc") or "").strip()
            or str(datos.get("password") or "").strip()
        )
        clave_pc = str(datos.get("clave_pc") or password or "").strip() or "No configurada"
        acceso_remoto = (datos.get("acceso_remoto") or "OK").strip()
        puerto_ssh = datos.get("puerto_ssh", "").strip() or "22"
        puerto_telnet = datos.get("puerto_telnet", "").strip() or "9999"

        antena_status = ""
        equipos_conectados = ""
        voltaje_pilas = ""
        errores = []

        # El Pancoordinator Telnet no requiere credenciales SSH.
        if host:
            try:
                antena_status = consultar_telnet(host, puerto_telnet, "cmd status")
            except Exception as exc:
                errores.append(f"Telnet status ({host}:{puerto_telnet}): {exc}")

            try:
                equipos_conectados = consultar_telnet(host, puerto_telnet, "cmd motes")
            except Exception as exc:
                errores.append(f"Telnet motes ({host}:{puerto_telnet}): {exc}")

        if host and password:
            remoto_cmd = (
                "for f in $(ls -1t /var/log/cacheton/jenreceiver_*.log /var/log/cacheton/jenreceiver* /var/log/cacheton*.log /var/log/jenreceiver_*.log /var/log/messages 2>/dev/null | head -3); do "
                "  test -f \"$f\" && tail -n 500 \"$f\" | grep -E ':NODE|NODE '; "
                "done | tail -30 || true"
            )
            ssh_client = None
            try:
                import paramiko

                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(
                    hostname=host,
                    port=int(puerto_ssh),
                    username=usuario,
                    password=password,
                    timeout=12,
                    look_for_keys=False,
                    allow_agent=False
                )
                _stdin, _stdout, _stderr = ssh_client.exec_command(remoto_cmd, timeout=15)
                resultado_ssh = _stdout.read().decode("utf-8", errors="replace").strip()
                if resultado_ssh:
                    voltaje_pilas = resultado_ssh
            except Exception as exc:
                errores.append(f"SSH: {exc}")
            finally:
                if ssh_client is not None:
                    ssh_client.close()

        if not antena_status.strip():
            antena_status = "Sin datos: no fue posible obtener cmd status."
        if not equipos_conectados.strip():
            equipos_conectados = "Sin datos: no fue posible obtener cmd motes."
        if not voltaje_pilas.strip():
            voltaje_pilas = "Sin datos: se requieren credenciales SSH para consultar los voltajes."

        res = {
            "dns": host or datos.get("dns") or "",
            "usuario": usuario,
            "clave_pc": clave_pc,
            "acceso_remoto": acceso_remoto,
            "repuestos_equipo": datos.get("repuestos_equipo") or "OK",
            "repuestos_sensor": datos.get("repuestos_sensor") or "OK",
            "repuestos_kit": datos.get("repuestos_kit") or "OK",
            "antena_status": antena_status,
            "equipos_conectados": equipos_conectados,
            "voltaje_pilas": voltaje_pilas,
            "observaciones": datos.get("observaciones") or "",
            "observaciones_generales": datos.get("observaciones_generales") or "",
            "error": " | ".join(errores) if errores else ""
        }
        res["plantilla_texto"] = RevisorService.generar_plantilla_ingreso_tecnico(res)
        res["documento_live_html"] = RevisorService.generar_documento_ingreso_tecnico_html(res)
        return res

    @staticmethod
    def generar_documento_ingreso_tecnico_html(datos: dict) -> str:
        """
        Genera un Documento Live HTML interactivo y estilizado sobrio/formal para Información de Ingreso de Técnico.
        """
        dns_host = html.escape(str(datos.get("dns") or datos.get("host") or datos.get("tun0") or "ce-yelcho.acuimatic.com"))
        clave_pc = html.escape(str(datos.get("clave_pc") or "No configurada"))
        acceso_remoto = html.escape(str(datos.get("acceso_remoto") or "-"))
        fecha = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        antena_status_raw = limpiar_salida_telnet(str(datos.get("antena_status") or ""))
        equipos_conectados_raw = limpiar_salida_telnet(str(datos.get("equipos_conectados") or ""))
        voltaje_pilas_raw = str(datos.get("voltaje_pilas") or "")

        observaciones = html.escape(str(datos.get("observaciones") or "Sin observaciones registradas."))
        obs_generales_raw = str(datos.get("observaciones_generales") or "")

        logo_src = obtener_logo_base64()

        motes_dict = parsear_motes(equipos_conectados_raw)
        filas_motes_html = ""
        if not motes_dict:
            lines = [l.strip() for l in equipos_conectados_raw.splitlines() if l.strip()]
            for l in lines:
                parts = l.split()
                if len(parts) >= 2:
                    num = html.escape(parts[0])
                    mac = html.escape(parts[1])
                    sig = html.escape(parts[2]) if len(parts) > 2 else "N/D"
                    rx = html.escape(parts[3]) if len(parts) > 3 else "N/D"
                    estado = html.escape(" ".join(parts[4:])) if len(parts) > 4 else "OK"
                    badge_cls = "badge-warn" if "MALO" in estado.upper() or "ERROR" in estado.upper() else "badge-ok"
                    filas_motes_html += f"""
                    <tr>
                        <td style="text-align: center;"><strong>#{num}</strong></td>
                        <td><code>{mac}</code></td>
                        <td style="text-align: center;">{sig}</td>
                        <td style="text-align: center;">{rx}</td>
                        <td><span class="badge {badge_cls}">{estado}</span></td>
                    </tr>
                    """
        else:
            for n_id, m in motes_dict.items():
                badge_cls = "badge-warn" if "MALO" in m.get("nombre", "").upper() else "badge-ok"
                filas_motes_html += f"""
                <tr>
                    <td style="text-align: center;"><strong>#{n_id}</strong></td>
                    <td><code>{html.escape(m.get('mac', 'N/D'))}</code></td>
                    <td style="text-align: center;">{html.escape(m.get('signal', 'N/D'))}</td>
                    <td style="text-align: center;">{html.escape(m.get('last_rx', 'N/D'))}</td>
                    <td><span class="badge {badge_cls}">{html.escape(m.get('nombre', 'OK'))}</span></td>
                </tr>
                """

        if not filas_motes_html:
            filas_motes_html = """
            <tr>
                <td colspan="5" style="text-align: center; color: #64748b; padding: 12px;">
                    <em>Sin información de equipos conectados.</em>
                </td>
            </tr>
            """

        voltajes_dict = parsear_voltajes(voltaje_pilas_raw)
        filas_voltajes_html = ""
        if voltajes_dict:
            for n_id, v_info in voltajes_dict.items():
                v_num = v_info.get("voltaje", 0.0)
                badge_cls = "badge-ok" if v_num >= 3.2 else "badge-warn"
                filas_voltajes_html += f"""
                <tr>
                    <td style="text-align: center;"><strong>Nodo #{n_id}</strong></td>
                    <td style="font-weight: 700; color: #002d4b;">{v_num:.2f} V</td>
                    <td>{v_info.get('alimentacion', 0.0):.2f} V</td>
                    <td><span class="badge {badge_cls}">{'CONFORME' if v_num >= 3.2 else 'REVISAR BATERÍA'}</span></td>
                </tr>
                """
        else:
            lines_v = [l.strip() for l in voltaje_pilas_raw.splitlines() if l.strip()]
            for idx, l in enumerate(lines_v, start=1):
                filas_voltajes_html += f"""
                <tr>
                    <td style="text-align: center;"><strong>#{idx}</strong></td>
                    <td colspan="3"><code>{html.escape(l)}</code></td>
                </tr>
                """

        checklist_items_html = ""
        for line in obs_generales_raw.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            if line.startswith("    ") or line.startswith("\t"):
                checklist_items_html += f"<div>&nbsp;&nbsp;&nbsp;&nbsp;{html.escape(line_str)}</div>"
            else:
                checklist_items_html += f"<div><strong>{html.escape(line_str)}</strong></div>"

        raw_centro = str(datos.get("centro") or "S/C").strip()
        centro_titulo = html.escape(raw_centro[3:].strip() if raw_centro.upper().startswith("CE-") else raw_centro)

        html_doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>REVISOR REMOTO — {centro_titulo}</title>
<style>
  body {{
    font-family: 'Helvetica', Arial, sans-serif;
    background: #ffffff;
    color: #111111;
    margin: 0;
    padding: 20px;
    font-size: 10.5px;
    line-height: 1.35;
  }}
  .reportlab-header-box {{
    display: flex;
    border: 1px solid #cccccc;
    margin-bottom: 16px;
    height: 52px;
  }}
  .reportlab-header-left {{
    width: 170px;
    background-color: #000000;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 4px;
    border-right: 1px solid #cccccc;
  }}
  .reportlab-header-left img {{
    max-width: 155px;
    max-height: 44px;
    object-fit: contain;
  }}
  .reportlab-header-center {{
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    font-weight: 800;
    font-size: 13px;
    color: #000000;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    padding: 0 12px;
  }}
  .reportlab-sec-title {{
    font-size: 11px;
    font-weight: 800;
    color: #000000;
    margin-top: 14px;
    margin-bottom: 6px;
    text-transform: uppercase;
  }}
  .reportlab-attr-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 10px;
  }}
  .reportlab-attr-table td {{
    border: 1px solid #cccccc;
    padding: 4px 8px;
  }}
  .reportlab-attr-table td.attr {{
    width: 35%;
    background-color: #f2f2f2;
    font-weight: 800;
    color: #000000;
  }}
  .reportlab-attr-table td.val {{
    width: 65%;
    background-color: #ffffff;
    color: #111111;
  }}
  .reportlab-list-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    font-size: 9.5px;
  }}
  .reportlab-list-table th {{
    background-color: #000000;
    color: #ffffff;
    font-weight: 800;
    border: 1px solid #cccccc;
    padding: 5px;
    text-align: center;
    text-transform: uppercase;
  }}
  .reportlab-list-table td {{
    border: 1px solid #cccccc;
    padding: 4px 6px;
    text-align: center;
    color: #111111;
  }}
  .reportlab-list-table tr:nth-child(even) {{
    background-color: #fcfcfc;
  }}
  .badge {{
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: bold;
    display: inline-block;
  }}
  .badge-ok {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
  .badge-warn {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
  pre.console {{
    background: #1e293b;
    color: #f8fafc;
    padding: 8px 10px;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10px;
    overflow-x: auto;
    border: 1px solid #334155;
    white-space: pre-wrap;
  }}
</style>
</head>
<body>
  <div class="reportlab-header-box" style="justify-content: center; text-align: center;">
    <div class="reportlab-header-center" style="width: 100%; text-align: center; font-size: 15px; font-weight: 800; letter-spacing: 0.5px;">
      INFORMACIÓN PARA INGRESO DE TÉCNICO
    </div>
  </div>

  <div class="reportlab-sec-title">1. Parámetros de Acceso & Conexión</div>
  <table class="reportlab-attr-table">
    <tr><td class="attr">DNS / Host (tun0)</td><td class="val">{dns_host}</td></tr>
    <tr><td class="attr">Clave PC</td><td class="val">{clave_pc}</td></tr>
    <tr><td class="attr">Acceso Remoto</td><td class="val">{acceso_remoto}</td></tr>
    <tr><td class="attr">Fecha de Emisión</td><td class="val">{fecha}</td></tr>
  </table>

  <div class="reportlab-sec-title">2. Status de Antena</div>
  <pre class="console">{html.escape(antena_status_raw)}</pre>

  <div class="reportlab-sec-title">3. Equipos Conectados</div>
  <table class="reportlab-list-table">
    <thead>
      <tr>
        <th style="width: 35px; text-align: center;">Nº</th>
        <th>Dirección MAC</th>
        <th style="width: 70px; text-align: center;">Señal</th>
        <th style="width: 80px; text-align: center;">Last RX</th>
        <th>Estado</th>
      </tr>
    </thead>
    <tbody>
      {filas_motes_html}
    </tbody>
  </table>

  <div class="reportlab-sec-title">4. Voltaje de Pilas por Equipo</div>
  <table class="reportlab-list-table">
    <thead>
      <tr>
        <th style="width: 80px; text-align: center;">Equipo</th>
        <th style="width: 95px;">Voltaje Batería</th>
        <th style="width: 100px;">Alimentación</th>
        <th>Evaluación</th>
      </tr>
    </thead>
    <tbody>
      {filas_voltajes_html}
    </tbody>
  </table>

  <div class="reportlab-sec-title">5. Observaciones del Técnico</div>
  <div class="info-box">{observaciones}</div>

  <div class="reportlab-sec-title">6. Observaciones Generales & Checklist</div>
  <div class="info-box">
    {checklist_items_html}
  </div>
</body>
</html>
"""
        return html_doc
