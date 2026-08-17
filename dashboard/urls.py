from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('correos-masivos/', views.correos_masivos, name='correos_masivos'),
    path('certificados/', views.certificados, name='certificados'),
    path('calendario/', views.calendario, name='calendario'),
    path('api/bitacora/actualizar/', views.actualizar_bitacora, name='actualizar_bitacora'),
    path('api/wiki/buscar/', views.buscar_wiki, name='buscar_wiki'),
]
