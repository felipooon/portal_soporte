from datetime import datetime
from dataclasses import asdict
from ..services.certificado_service import CertificadoService
from .certificado_menu import CertificadoMenu
from .ui import (
    limpiar_pantalla, caja, banner_bienvenida, opcion_menu,
    separador, breadcrumb, prompt, notificacion_exito,
    notificacion_error, notificacion_info, encabezado_pegar,
    item_lista, Color, Icono
)


class Menu:

    def __init__(self):
        self.service = CertificadoService()

    def mostrar(self):

        while True:

            limpiar_pantalla()
            print(banner_bienvenida())
            print(breadcrumb("Inicio"))
            print()

            print(opcion_menu("1", "Nuevo certificado"))
            print(opcion_menu("2", "Nuevo certificado (auto-rellenado)"))
            print(opcion_menu("3", "Abrir certificado existente"))
            print()
            print(separador())
            print(opcion_menu("4", "Salir"))
            print()

            opcion = input(prompt()).strip()

            if opcion == "1":
                self.nuevo_certificado()

            elif opcion == "2":
                self.nuevo_certificado_autofill()

            elif opcion == "3":
                self.abrir_certificado()

            elif opcion == "4":
                limpiar_pantalla()
                print(f"\n  {Color.DIM}Hasta luego.{Color.RESET}\n")
                break

            else:
                print(notificacion_error("Opción inválida"))
                input(f"  {Color.DIM}Presione Enter para continuar...{Color.RESET}")

    def nuevo_certificado(self):

        limpiar_pantalla()
        print()
        print(caja(f"{Color.BOLD}Nuevo Certificado{Color.RESET}"))
        print(breadcrumb("Inicio", "Nuevo Certificado"))
        print()

        location = input(
            prompt("Location (ej. ca-ahoni)")
        ).strip().lower()

        nombre_centro = input(
            prompt("Nombre centro (ej. CA-AHONI)")
        ).strip()

        if not location:
            print(notificacion_error("Centro inválido"))
            input(f"  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
            return

        año = datetime.now().year

        certificado = (
            CertificadoService
            .crear_certificado(
                location,
                nombre_centro
            )
        )

        ruta = self.service.guardar_certificado(
            certificado=certificado,
            location=location,
            año=año
        )

        print(notificacion_exito("Certificado creado exitosamente"))
        print(f"  {Color.DIM}{ruta}{Color.RESET}")
        input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")

    def nuevo_certificado_autofill(self):
        limpiar_pantalla()
        print()

        instrucciones = [
            "Copie y pegue la salida de consola de uno o varios comandos:",
            "  'cmd status'   → Versión, MAC y Pan ID de antena",
            "  'cmd motes'    → Lista de motes",
            "  'ifconfig'     → Interfaz, MAC Ethernet, IP LAN y VPN",
            "  'hostnamectl'  → SO, Marca, Modelo y Categoría",
            "  JSON config    → Cacheton / jenreceiver",
            "",
            "Ingrese 'FIN' o presione Enter dos veces al terminar",
        ]
        print(encabezado_pegar("NUEVO CERTIFICADO — AUTO-RELLENADO", instrucciones))
        print(breadcrumb("Inicio", "Nuevo (Auto-rellenado)"))
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

        texto = "\n".join(lineas)

        cert_temp = {}
        from certificado.utils.autofill import procesar_autofill
        res = procesar_autofill(cert_temp, texto)

        location = cert_temp.get("datos_generales", {}).get("location", "").strip().lower()
        nombre_centro = cert_temp.get("datos_generales", {}).get("nombre_centro", "").strip()

        if not location:
            print()
            print(caja(f"{Color.BOLD}Datos de Identificación{Color.RESET}"))
            print()
            location = input(prompt("Location (ej. ca-ahoni)")).strip().lower()
            nombre_centro = input(prompt("Nombre centro (ej. CA-AHONI)")).strip()

        if not location:
            print(notificacion_error("Creación cancelada: Location no especificada."))
            input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
            return

        if not nombre_centro:
            nombre_centro = location.upper()

        año = datetime.now().year
        certificado = CertificadoService.crear_certificado(location, nombre_centro)

        if hasattr(certificado, "__dataclass_fields__"):
            cert_dict = asdict(certificado)
        else:
            cert_dict = certificado

        procesar_autofill(cert_dict, texto)

        ruta = self.service.guardar_certificado(
            certificado=cert_dict,
            location=location,
            año=año
        )

        print()
        print(notificacion_exito(f"Certificado para '{location.upper()}' creado y auto-rellenado"))
        if res["exito"]:
            for cambio in res["resumen"]:
                print(f"    {Color.DIM}{Icono.ARROW} {cambio}{Color.RESET}")
        print(f"  {Color.DIM}Guardado en: {ruta}{Color.RESET}")
        print()
        input(f"  {Color.DIM}Presione Enter para continuar al certificado...{Color.RESET}")

        menu_certificado = CertificadoMenu(
            certificado=cert_dict,
            centro=location,
            año=año
        )
        menu_certificado.mostrar()

    def abrir_certificado(self):

        limpiar_pantalla()
        print()
        print(caja(f"{Color.BOLD}Abrir Certificado{Color.RESET}"))
        print(breadcrumb("Inicio", "Abrir Certificado"))
        print()

        año = datetime.now().year

        certificados = self.service.listar_certificados(año)

        if not certificados:
            print(notificacion_advertencia("No existen certificados"))
            input(f"\n  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
            return

        for indice, nombre in enumerate(certificados, start=1):
            print(item_lista(indice, nombre))

        print()

        seleccion = input(
            prompt("Seleccione certificado (ENTER para volver)")
        ).strip()

        if not seleccion:
            return

        try:

            indice = int(seleccion) - 1

            location = certificados[indice]

        except (ValueError, IndexError):

            print(notificacion_error("Selección inválida"))
            input(f"  {Color.DIM}Presione Enter para continuar...{Color.RESET}")
            return

        certificado = self.service.cargar_certificado(
            location=location,
            año=datetime.now().year
        )

        menu_certificado = CertificadoMenu(
            certificado=certificado,
            centro=location,
            año=año
        )

        menu_certificado.mostrar()