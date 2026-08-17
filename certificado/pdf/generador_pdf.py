from dataclasses import asdict
from pathlib import Path

from .plantilla import NumberedCanvas, ALTO_PAGINA
from .seccion_datos_generales import agregar_datos_generales
from .seccion_infraestructura import agregar_infraestructura
from .seccion_estacion_camara import agregar_estacion_camara
from .seccion_ubicaciones import agregar_equipos_instalados
from .seccion_activacion import agregar_validacion_operativa, agregar_checklist_validacion
from .seccion_observaciones import agregar_observaciones
from .seccion_evidencias import agregar_evidencias
from .seccion_configuracion_alarmas import agregar_configuracion_alarmas


class GeneradorPDF:

    def verificar_espacio(self, pdf, y, espacio_requerido=70):
        if y - espacio_requerido < 45:
            pdf.showPage()
            return ALTO_PAGINA - 90
        return y

    def generar(self, certificado, archivo_salida, carpeta_evidencias=None):
        if hasattr(certificado, "__dataclass_fields__"):
            # pyrefly: ignore [bad-argument-type]
            certificado = asdict(certificado)

        ruta_salida = Path(archivo_salida)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)

        datos_gen = certificado.get("datos_generales", {})
        num_ficha = str(datos_gen.get("numero_ficha") or datos_gen.get("location") or "001").upper()
        codigo_registro = num_ficha if num_ficha.startswith("DS-") else f"DS-{num_ficha}"

        posible_dir = ruta_salida.parent / "evidencias"
        if not carpeta_evidencias:
            carpeta_evidencias = posible_dir

        # Bloqueo y protección del PDF contra ediciones y modificaciones no autorizadas
        from reportlab.lib.pdfencrypt import StandardEncryption
        clave_propietario = f"InnovexProtect_{codigo_registro}_2026"
        pdf_lock = StandardEncryption(
            userPassword="",
            ownerPassword=clave_propietario,
            canPrint=1,
            canModify=0,
            canCopy=0,
            canAnnotate=0,
            strength=128
        )

        pdf = NumberedCanvas(
            str(ruta_salida),
            codigo_registro=codigo_registro,
            encrypt=pdf_lock
        )
        pdf.setTitle("Validación de Instalación")

        y = ALTO_PAGINA - 90

        # 1. Información general del centro
        y = self.verificar_espacio(pdf, y, 180)
        y = agregar_datos_generales(pdf, certificado.get("datos_generales", {}), y)

        # 2. Computador y configuración de red
        y = self.verificar_espacio(pdf, y, 160)
        y = agregar_infraestructura(pdf, certificado.get("infraestructura", {}), y, certificado=certificado)

        # 3. Antena, estación meteorológica y cámara
        y = self.verificar_espacio(pdf, y, 180)
        y = agregar_estacion_camara(
            pdf,
            certificado.get("estacion_camara", {}),
            certificado.get("monitoreo_abiotico", {}),
            y
        )

        # 4. Equipos instalados y 5. Repuestos
        y = self.verificar_espacio(pdf, y, 160)
        y = agregar_equipos_instalados(
            pdf,
            certificado.get("ubicaciones", []),
            certificado.get("equipos_repuesto") or certificado.get("repuestos", []),
            y,
            certificado=certificado
        )

        # 6. Validación operativa
        y = self.verificar_espacio(pdf, y, 180)
        y = agregar_validacion_operativa(pdf, certificado.get("activacion", {}), y, certificado=certificado)

        # 7. Configuración de alarmas
        y = self.verificar_espacio(pdf, y, 160)
        y = agregar_configuracion_alarmas(pdf, certificado, y)

        # 8. Observaciones y notas
        y = self.verificar_espacio(pdf, y, 60)
        y = agregar_observaciones(pdf, certificado.get("observaciones", ""), y)

        # 9. Checklist de validación
        y = self.verificar_espacio(pdf, y, 180)
        y = agregar_checklist_validacion(pdf, certificado.get("activacion", {}), y)

        # 10. Registro fotográfico (Evidencias al final del informe)
        y = agregar_evidencias(
            pdf,
            certificado.get("evidencias", []),
            y,
            carpeta_evidencias=carpeta_evidencias
        )

        pdf.save()