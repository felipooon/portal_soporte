from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='certificado_index'),
    path('api/list', views.api_list, name='api_list'),
    path('api/pdf_preview/<int:anio>/<str:location>/<str:nombre_pdf>', views.api_pdf_preview, name='api_pdf_preview'),
    path('api/autofill', views.api_autofill, name='api_autofill'),
    path('api/save', views.api_save, name='api_save'),
    path('api/generate_pdf', views.api_generate_pdf, name='api_generate_pdf'),
    path('api/load', views.api_load, name='api_load'),
    path('api/delete', views.api_delete, name='api_delete'),
    path('api/upload_evidencia', views.api_upload_evidencia, name='api_upload_evidencia'),
    path('api/upload_alarmas', views.api_upload_alarmas, name='api_upload_alarmas'),
    path('api/parse_alarmas_texto', views.api_parse_alarmas_texto, name='api_parse_alarmas_texto'),
    path('api/revisor/verificar', views.api_revisor_verificar, name='api_revisor_verificar'),
    path('api/revisor/generar_plantilla', views.api_revisor_generar_plantilla, name='api_revisor_generar_plantilla'),
    path('api/revisor/ingreso_tecnico', views.api_revisor_ingreso_tecnico, name='api_revisor_ingreso_tecnico'),
    path('api/revisor/generar_plantilla_ingreso', views.api_revisor_generar_plantilla_ingreso, name='api_revisor_generar_plantilla_ingreso'),
]
