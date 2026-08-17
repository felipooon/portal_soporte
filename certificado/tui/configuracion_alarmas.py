from pathlib import Path
from certificado.utils.excel_parser import parsear_alarmas_excel
from certificado.services.certificado_service import CertificadoService
from .ui import (
    limpiar_pantalla, caja, separador, breadcrumb,
    opcion_menu, prompt, texto_vacio, item_lista,
    encabezado_tabla, fila_tabla,
    notificacion_exito, notificacion_error, notificacion_advertencia,
    notificacion_info, Color, Icono
)


class ConfiguracionAlarmasScreen:

    def __init__(self, certificado: dict):
        self.certificado = certificado
        if "configuracion_alarmas" not in self.certificado:
            self.certificado["configuracion_alarmas"] = []

    def mostrar(self):
        while True:
            alarmas = self.certificado["configuracion_alarmas"]

            limpiar_pantalla()
            print()
            print(caja(f"{Color.BOLD}CONFIGURACIÓN DE ALARMAS{Color.RESET}"))
            print(breadcrumb("Inicio", "Certificado", "Config. Alarmas"))
            print()

            if not alarmas:
                print(texto_vacio("No existen alarmas configuradas."))
                print(f"  {Color.DIM}Tip: Presione 'C' para cargar automáticamente desde Excel (.xlsx).{Color.RESET}")
            else:
                print(f"  {Color.DIM}{len(alarmas)} alarmas configuradas{Color.RESET}")
                print()
                print(encabezado_tabla(
                    ("N°", 3), ("Status", 10), ("Equipo", 10),
                    ("Sensor", 22), ("Medición", 8), ("Min", 5), ("Max", 5)
                ))
                for idx, al in enumerate(alarmas, start=1):
                    st = str(al.get("status", "Activada"))[:10]
                    eq = str(al.get("equipo", "-"))[:10]
                    sn = str(al.get("sensor", "-"))[:22]
                    med = str(al.get("medicion", "-"))[:8]
                    c_min = str(al.get("conf_min", "-"))[:5]
                    c_max = str(al.get("conf_max", "-"))[:5]
                    print(fila_tabla(
                        (idx, 3), (st, 10), (eq, 10),
                        (sn, 22), (med, 8), (c_min, 5), (c_max, 5)
                    ))

            print()
            print(separador())
            print()
            print(opcion_menu("C", "Cargar desde Excel (.xlsx / .ods)"))
            print(opcion_menu("P", "Pegar alarmas desde texto (Copiar y Pegar)"))
            print(opcion_menu("X", "Eliminar alarma"))
            print(opcion_menu("V", "Volver"))
            print()

            opcion = input(prompt()).strip().upper()

            if opcion == "C":
                self.cargar_excel()
            elif opcion == "P":
                self.pegar_texto()
            elif opcion == "X":
                self.eliminar()
            elif opcion == "V":
                break
            else:
                print(notificacion_error("Opción inválida."))
                input(f"  {Color.DIM}Presione Enter...{Color.RESET}")

    def pegar_texto(self):
        limpiar_pantalla()
        print()
        print(caja(f"{Color.BOLD}Pegar Alarmas desde Texto / Portapapeles{Color.RESET}"))
        print(breadcrumb("Inicio", "Certificado", "Config. Alarmas", "Pegar Texto"))
        print()
        print(f"  {Color.DIM}Pegue las filas copiadas desde Excel, Web o consola.{Color.RESET}")
        print(f"  {Color.DIM}Columnas esperadas: Estado, Usuario, Mínima, Máxima, Medicion Especifica, Centros, Equipo, Sensor{Color.RESET}")
        print(f"  {Color.DIM}Escriba 'FIN' en una línea nueva cuando termine de pegar.{Color.RESET}")
        print()

        lineas = []
        while True:
            try:
                linea = input()
                if linea.strip().upper() == "FIN":
                    break
                lineas.append(linea)
            except (EOFError, KeyboardInterrupt):
                break

        texto_pegado = "\n".join(lineas)
        if not texto_pegado.strip():
            print(notificacion_advertencia("No se ingresó texto."))
            input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
            return

        from certificado.utils.excel_parser import parsear_alarmas_texto
        alarmas_leidas = parsear_alarmas_texto(texto_pegado)
        if not alarmas_leidas:
            print(notificacion_error("No se pudieron parsear filas de alarmas válidas."))
            input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
            return

        self.certificado["configuracion_alarmas"].extend(alarmas_leidas)
        print(notificacion_exito(f"Se agregaron {len(alarmas_leidas)} alarmas exitosamente."))
        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")

    def cargar_excel(self):
        limpiar_pantalla()
        print()
        print(caja(f"{Color.BOLD}Cargar Alarmas desde Excel{Color.RESET}"))
        print()

        datos_gen = self.certificado.get("datos_generales", {})
        location = datos_gen.get("location", "ca-ahoni")
        nombre_centro = datos_gen.get("nombre_centro", location)
        año = 2026

        dir_entrada = CertificadoService.obtener_carpeta_entrada()
        dir_historico = CertificadoService.obtener_carpeta_evidencias(location, año)

        archivos_planillas = []
        for d in [dir_entrada, dir_historico]:
            if d.exists():
                for f in d.iterdir():
                    if f.is_file() and f.suffix.lower() in [".ods", ".xlsx"] and not f.name.startswith(".") and not f.name.startswith(".~lock"):
                        if f not in archivos_planillas:
                            archivos_planillas.append(f)

        ruta_cargar = None
        if archivos_planillas:
            print(f"  {Color.BOLD}Planillas disponibles en evidencias:{Color.RESET}")
            print()
            for idx, f in enumerate(archivos_planillas, start=1):
                print(item_lista(idx, f.name))
            print()
            opc = input(prompt("Seleccione número de archivo (Enter para el primero)")).strip()
            if not opc and len(archivos_planillas) >= 1:
                ruta_cargar = archivos_planillas[0]
            elif opc.isdigit() and 1 <= int(opc) <= len(archivos_planillas):
                ruta_cargar = archivos_planillas[int(opc) - 1]

        if not ruta_cargar:
            entrada = input(prompt("Ruta completa o relativa del archivo (.ods / .xlsx)")).strip()
            if not entrada:
                print(notificacion_advertencia("Operación cancelada."))
                return
            ruta_cargar = Path(entrada)

        alarmas_leidas = parsear_alarmas_excel(ruta_cargar, nombre_centro=nombre_centro)
        if not alarmas_leidas:
            print(notificacion_error(f"No se pudieron extraer alarmas desde {ruta_cargar.name}."))
            print(notificacion_info("Verifique que el archivo contenga columnas de alarmas."))
            input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
            return

        self.certificado["configuracion_alarmas"] = alarmas_leidas
        print(notificacion_exito(f"Se cargaron {len(alarmas_leidas)} alarmas desde '{ruta_cargar.name}'."))
        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")

    def eliminar(self):
        alarmas = self.certificado["configuracion_alarmas"]
        if not alarmas:
            print(notificacion_advertencia("No existen alarmas para eliminar."))
            input(f"  {Color.DIM}Presione Enter...{Color.RESET}")
            return

        print()
        sel = input(prompt("Número de alarma a eliminar")).strip()
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(alarmas):
                eliminada = alarmas.pop(idx)
                print(notificacion_exito(f"Alarma de {eliminada.get('sensor', '')} eliminada."))
            else:
                print(notificacion_error("Selección inválida."))
        else:
            print(notificacion_error("Selección inválida."))
