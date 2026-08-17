from certificado.utils.input_helpers import (
    input_con_control,
    CancelarEdicionException,
    GuardarAvanceException
)
from .ui import (
    limpiar_pantalla, caja, separador, breadcrumb,
    opcion_menu, prompt, encabezado_pegar, encabezado_tabla, fila_tabla,
    item_lista, texto_vacio,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    Color, Icono
)


def parse_cmd_motes(texto: str) -> list[dict]:
    """Parsea la salida de texto plano del comando 'cmd motes' / 'cmd status' / logs."""
    import re
    motes = []
    macs_vistas = set()

    lineas = texto.strip().splitlines()
    for linea in lineas:
        linea_str = linea.strip()
        if not linea_str:
            continue

        # Encabezados de tabla
        if "mote" in linea_str.lower() and "mac" in linea_str.lower() and "signal" in linea_str.lower():
            continue

        partes = linea_str.split()
        if len(partes) >= 3:
            # Buscar la posición de la MAC en las partes de la línea
            mac_idx = -1
            for i, p in enumerate(partes):
                p_clean = p.strip(",;()[]")
                if re.match(r"^00:15:8[dD]:[0-9a-fA-F:]{11}$", p_clean) or (":" in p_clean and len(p_clean) == 23):
                    mac_idx = i
                    break
                elif re.match(r"^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){7}$", p_clean):
                    mac_idx = i
                    break

            if mac_idx != -1:
                mac = partes[mac_idx].strip(",;()[]").upper()
                if mac in macs_vistas:
                    continue
                macs_vistas.add(mac)

                mote = partes[mac_idx - 1] if mac_idx > 0 and partes[mac_idx - 1].isdigit() else str(len(motes) + 1)
                signal = partes[mac_idx + 1] if len(partes) > mac_idx + 1 else "N/D"
                last_rx = partes[mac_idx + 2] if len(partes) > mac_idx + 2 else "N/D"
                name = partes[mac_idx + 3] if len(partes) > mac_idx + 3 else ""

                if name.isdigit():
                    asociacion = f"Equipo {name}"
                elif name:
                    asociacion = name
                else:
                    asociacion = f"Equipo {mote}"

                motes.append({
                    "mote": mote,
                    "mac": mac,
                    "signal": signal,
                    "last_rx": last_rx,
                    "name": name,
                    "asociacion": asociacion
                })
                continue

        # Regex fallback para cualquier MAC Jennic encontrada en la línea
        matches_mac = re.findall(r"(00:15:8[dD]:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})", linea_str, re.IGNORECASE)
        for mac_found in matches_mac:
            mac_u = mac_found.upper()
            if mac_u not in macs_vistas:
                macs_vistas.add(mac_u)
                mote_num = str(len(motes) + 1)
                motes.append({
                    "mote": mote_num,
                    "mac": mac_u,
                    "signal": "N/D",
                    "last_rx": "N/D",
                    "name": "",
                    "asociacion": f"Equipo {mote_num}"
                })

    return motes


class MotesScreen:

    def __init__(self, certificado: dict):
        self.certificado = certificado

        if "motes" not in self.certificado:
            self.certificado["motes"] = []

    def mostrar(self):
        while True:
            motes = self.certificado["motes"]

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}EQUIPOS JENNIC (cmd motes / cmd status){Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Activación", "Equipos Jennic"))
            print()

            if not motes:
                print(texto_vacio("No existen registros de motes / equipos Jennic."))
            else:
                print(f"  {Color.DIM}{len(motes)} equipos registrados{Color.RESET}")
                print()
                print(encabezado_tabla(
                    ("Mote", 6), ("MAC", 26), ("Señal", 10), ("LastRx", 8), ("Asociación", 15)
                ))
                for idx, m in enumerate(motes, start=1):
                    mote = m.get("mote", str(idx))
                    mac = m.get("mac", "-")
                    signal = m.get("signal", "-")
                    last_rx = m.get("last_rx", "-")
                    asoc = m.get("asociacion", "-")
                    print(fila_tabla(
                        (mote, 6), (mac, 26), (signal, 10), (last_rx, 8), (asoc, 15)
                    ))

            print()
            print(separador())
            print()
            print(opcion_menu("P", "Pegar salida de 'cmd motes / cmd status'"))
            print(opcion_menu("A", "Agregar mote manualmente"))
            print(opcion_menu("X", "Eliminar un mote"))
            print(opcion_menu("C", "Limpiar todos los motes"))
            print(opcion_menu("V", "Volver"))
            print()

            opcion = input(prompt()).strip().upper()

            if opcion == "P":
                self.pegar_salida_cmd_motes()

            elif opcion == "A":
                self.agregar_mote()

            elif opcion == "X":
                self.eliminar_mote()

            elif opcion == "C":
                self.limpiar_motes()

            elif opcion == "V":
                break

            else:
                print(notificacion_error("Opción inválida."))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def pegar_salida_cmd_motes(self):
        limpiar_pantalla()
        print()

        instrucciones = [
            "Copie y pegue la salida directamente de la consola.",
            "Ingrese 'FIN' o deje una línea vacía al terminar.",
        ]
        print(encabezado_pegar("PEGAR SALIDA DE 'cmd motes / cmd status'", instrucciones))
        print()

        lineas = []
        try:
            while True:
                linea = input()
                if linea.strip().upper() == "FIN":
                    break
                if not linea.strip() and lineas and not lineas[-1].strip():
                    break
                lineas.append(linea)
        except (EOFError, KeyboardInterrupt):
            pass

        texto_pegado = "\n".join(lineas)
        motes_parseados = parse_cmd_motes(texto_pegado)

        if not motes_parseados:
            print(notificacion_error("No se pudieron extraer datos de la salida pegada."))
            print(f"  {Color.DIM}Asegúrese de copiar las columnas Mote, MAC, Signal, LastRx, Name.{Color.RESET}")
        else:
            self.certificado["motes"] = motes_parseados
            print(notificacion_exito(f"Se registraron exitosamente {len(motes_parseados)} motes / equipos Jennic."))

        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")

    def agregar_mote(self):
        limpiar_pantalla()
        print()
        print(caja(f"{Color.BOLD}AGREGAR MOTE MANUALMENTE{Color.RESET}"))
        print(f"  {Color.DIM}Tip: Ingrese ':c' o 'CANCELAR' para anular{Color.RESET}")
        print()

        try:
            mote = input_con_control("Número Mote (ej. 1): ").strip()
            if not mote:
                return

            mac = input_con_control("Dirección MAC (ej. 00:15:8D:00:08:5D:5E:BA): ").strip()
            signal = input_con_control("Señal / Signal (ej. 84:90): ").strip()
            last_rx = input_con_control("LastRx en seg. (ej. 14): ").strip()
            asoc = input_con_control("Asociación / Equipo (ej. Equipo 9): ").strip()

            item = {
                "mote": mote,
                "mac": mac,
                "signal": signal,
                "last_rx": last_rx,
                "name": asoc,
                "asociacion": asoc if asoc.lower().startswith("equipo") else f"Equipo {asoc}" if asoc.isdigit() else asoc
            }

            self.certificado["motes"].append(item)
            print(notificacion_exito(f"Mote {mote} agregado."))

        except (CancelarEdicionException, GuardarAvanceException):
            print(notificacion_advertencia("Alta de mote cancelada."))

    def eliminar_mote(self):
        motes = self.certificado["motes"]
        if not motes:
            print(notificacion_advertencia("No hay motes registrados."))
            input(f"  {Color.DIM}Presione Enter...{Color.RESET}")
            return

        print()
        for idx, m in enumerate(motes, start=1):
            print(item_lista(idx, f"Mote {m.get('mote', idx)} — MAC {m.get('mac', '')}"))

        print()
        sel = input(prompt("Número a eliminar")).strip()
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(motes):
                eliminado = motes.pop(idx)
                print(notificacion_exito(f"Mote {eliminado.get('mote', '')} eliminado."))
            else:
                print(notificacion_error("Selección inválida."))
        else:
            print(notificacion_error("Selección inválida."))

    def limpiar_motes(self):
        conf = input(
            f"  {Color.YELLOW}{Icono.BULLET} ¿Está seguro de eliminar TODOS los motes? (S/N): {Color.RESET}"
        ).strip().upper()
        if conf == "S":
            self.certificado["motes"] = []
            print(notificacion_exito("Todos los motes fueron eliminados."))
        else:
            print(notificacion_advertencia("Operación cancelada."))
