import json
import base64
from pathlib import Path
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from certificado.services.certificado_service import CertificadoService
from certificado.services.revisor_service import RevisorService
from certificado.utils.autofill import procesar_autofill
from certificado.utils.excel_parser import parsear_alarmas_excel, parsear_alarmas_texto
from certificado.pdf.generador_pdf import GeneradorPDF

from django.template.loader import render_to_string
from django.http import HttpResponse

def index(request):
    html = render_to_string('certificado/index.html', request=request)
    # Inyectar la hoja de estilos de unificación visual sin tocar el HTML original
    css_override = '<link rel="stylesheet" id="portal-style-override" href="/static/css/certificado_override.css">'
    html = html.replace('</head>', f'  {css_override}\n</head>')
    
    # Inyectar script JS para conmutar el tema
    js_script = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const overrideLink = document.getElementById('portal-style-override');
        const toggleBtn = document.getElementById('btnTogglePortalTheme');
        if (overrideLink && toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                if (overrideLink.disabled) {
                    overrideLink.disabled = false;
                    toggleBtn.innerText = '🎨 Estilo: Portal';
                } else {
                    overrideLink.disabled = true;
                    toggleBtn.innerText = '🎨 Estilo: Corporativo';
                }
            });
        }
    });
    </script>
    """
    html = html.replace('</body>', f'  {js_script}\n</body>')
    
    # Inyectar dinámicamente el botón de volver al portal y el de cambiar tema
    boton_volver = '<a href="/" class="btn btn-secondary btn-small">🏠 Volver al Menú</a>'
    boton_tema = '<button class="btn btn-secondary btn-small" id="btnTogglePortalTheme" title="Cambiar a Estilo Corporativo">🎨 Estilo: Portal</button>'
    html = html.replace(
        '<div class="header-actions">',
        f'<div class="header-actions">\n      {boton_volver}\n      {boton_tema}'
    )
    return HttpResponse(html)

@require_http_methods(["GET"])
def api_list(request):
    try:
        año = int(request.GET.get("año", datetime.now().year))
        certificados = CertificadoService.listar_certificados(año)
        return JsonResponse({"status": "ok", "año": año, "certificados": certificados})
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@require_http_methods(["GET"])
def api_pdf_preview(request, anio, location, nombre_pdf):
    dir_location = Path("storage/certificados") / str(anio) / location
    posibles = [
        dir_location / nombre_pdf,
        dir_location / "certificado.pdf"
    ]
    for p in posibles:
        if p.exists() and p.is_file():
            return FileResponse(open(p, 'rb'), content_type='application/pdf', filename=nombre_pdf)
    raise Http404("PDF no encontrado")

@csrf_exempt
@require_http_methods(["POST"])
def api_autofill(request):
    try:
        body = json.loads(request.body)
        texto = body.get("texto", "")
        certificado_actual = body.get("certificado", {})
        resultado = procesar_autofill(certificado_actual, texto)
        return JsonResponse({"status": "ok", "certificado": certificado_actual, "resumen": resultado.get("resumen", [])})
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_save(request):
    try:
        body = json.loads(request.body)
        certificado = body.get("certificado", {})
        datos_gen = certificado.get("datos_generales", {})
        location = datos_gen.get("location") or "sin_location"
        año = datetime.now().year
        
        ruta_json = CertificadoService.guardar_certificado(certificado, location, año)
        CertificadoService.copiar_evidencias_a_certificado(location, año)
        
        return JsonResponse({
            "status": "ok",
            "mensaje": "Certificado guardado correctamente",
            "ruta": str(ruta_json),
            "location": location,
            "año": año
        })
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_generate_pdf(request):
    try:
        body = json.loads(request.body)
        certificado = body.get("certificado", {})
        datos_gen = certificado.get("datos_generales", {})
        location = datos_gen.get("location") or "sin_location"
        año = datetime.now().year

        dir_cert = Path("storage/certificados") / str(año) / location
        dir_cert.mkdir(parents=True, exist_ok=True)
        
        ruta_json = CertificadoService.guardar_certificado(certificado, location, año)
        CertificadoService.copiar_evidencias_a_certificado(location, año)

        nombre_pdf = f"certificado_inst_{location}.pdf"
        ruta_pdf = dir_cert / nombre_pdf
        dir_evidencias = dir_cert / "evidencias"

        GeneradorPDF().generar(
            certificado,
            str(ruta_pdf),
            carpeta_evidencias=dir_evidencias if dir_evidencias.exists() else None
        )

        pdf_preview_url = f"/certificado/api/pdf_preview/{año}/{location}/{nombre_pdf}"
        
        return JsonResponse({
            "status": "ok",
            "mensaje": "PDF generado con éxito",
            "ruta_pdf": str(ruta_pdf),
            "pdf_preview_url": pdf_preview_url
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_load(request):
    try:
        body = json.loads(request.body)
        location = body.get("location")
        año = int(body.get("año", datetime.now().year))
        if not location:
            return JsonResponse({"status": "error", "mensaje": "Location es requerido"}, status=400)

        try:
            cert_data = CertificadoService.cargar_certificado(location, año)
            return JsonResponse({"status": "ok", "certificado": cert_data})
        except FileNotFoundError:
            return JsonResponse({"status": "error", "mensaje": f"No se encontró certificado para {location}"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_delete(request):
    try:
        body = json.loads(request.body)
        location = body.get("location") or body.get("datos_generales", {}).get("location")
        año = int(body.get("año", datetime.now().year))
        if not location:
            return JsonResponse({"status": "error", "mensaje": "Location es requerido"}, status=400)

        exito = CertificadoService.eliminar_certificado(location, año)
        if exito:
            return JsonResponse({
                "status": "ok",
                "mensaje": f"Certificado de {location} eliminado correctamente",
                "location": location
            })
        else:
            return JsonResponse({"status": "error", "mensaje": f"No se encontró el certificado de {location}"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_upload_evidencia(request):
    try:
        body = json.loads(request.body)
        nombre = body.get("nombre", "foto.jpg")
        base64_data = body.get("base64", "")
        location = body.get("location", "sin_location")
        
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]
            
        file_bytes = base64.b64decode(base64_data)
        
        dir_ev = Path("storage/certificados/2026") / location / "evidencias"
        dir_ev.mkdir(parents=True, exist_ok=True)
        
        dest_file = dir_ev / nombre
        dest_file.write_bytes(file_bytes)
        
        return JsonResponse({
            "status": "ok",
            "mensaje": "Evidencia subida correctamente",
            "ruta": str(dest_file),
            "nombre": nombre
        })
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_upload_alarmas(request):
    try:
        body = json.loads(request.body)
        nombre = body.get("nombre", "alarmas.xlsx")
        base64_data = body.get("base64", "")
        location = body.get("location", "sin_location")
        
        if "," in base64_data:
            base64_data = base64_data.split(",", 1)[1]
            
        file_bytes = base64.b64decode(base64_data)
        dir_ev = Path("storage/certificados/2026") / location / "evidencias"
        dir_ev.mkdir(parents=True, exist_ok=True)
        
        dest_file = dir_ev / nombre
        dest_file.write_bytes(file_bytes)
        
        alarmas = parsear_alarmas_excel(dest_file)
        return JsonResponse({
            "status": "ok",
            "mensaje": "Planilla de alarmas procesada",
            "alarmas": alarmas
        })
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_parse_alarmas_texto(request):
    try:
        body = json.loads(request.body)
        texto = body.get("texto", "")
        alarmas = parsear_alarmas_texto(texto)
        return JsonResponse({
            "status": "ok",
            "mensaje": f"{len(alarmas)} alarmas procesadas",
            "alarmas": alarmas
        })
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_revisor_verificar(request):
    try:
        body = json.loads(request.body)
        resultado = RevisorService.verificar_equipo(body)
        return JsonResponse({"status": "ok", "resultado": resultado})
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_revisor_generar_plantilla(request):
    try:
        body = json.loads(request.body)
        plantilla = RevisorService.generar_plantilla_texto(body)
        return JsonResponse({"status": "ok", "plantilla_texto": plantilla})
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_revisor_ingreso_tecnico(request):
    try:
        body = json.loads(request.body)
        resultado = RevisorService.consultar_ingreso_tecnico_remoto(body)
        return JsonResponse({"status": "ok", "resultado": resultado})
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_revisor_generar_plantilla_ingreso(request):
    try:
        body = json.loads(request.body)
        plantilla = RevisorService.generar_plantilla_ingreso_tecnico(body)
        html_doc = RevisorService.generar_documento_ingreso_tecnico_html(body)
        return JsonResponse({
            "status": "ok",
            "plantilla_texto": plantilla,
            "documento_live_html": html_doc
        })
    except Exception as e:
        return JsonResponse({"status": "error", "mensaje": str(e)}, status=500)
