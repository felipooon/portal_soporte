from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('alternativo', views.index_alternativo, name='dashboard_alternativo'),
    path('pizarra-embed', views.pizarra_embed, name='pizarra_embed'),
    path('planillas-drive', views.planillas_embed, name='planillas_embed'),
    path('correos-masivos/', views.correos_masivos, name='correos_masivos'),
    path('correos-masivos/gestionar/', views.gestionar_correos, name='gestionar_correos'),
    path('certificados/', views.certificados, name='certificados'),
    path('calendario/', views.calendario, name='calendario'),
    path('api/bitacora/actualizar/', views.actualizar_bitacora, name='actualizar_bitacora'),
    path('api/wiki/buscar/', views.buscar_wiki, name='buscar_wiki'),
    path('trac/', views.trac_wiki, name='trac_wiki'),
    path('music/', views.music, name='music'),
    path('api/music/control/', views.music_control, name='music_control'),
    path('api/music/status/', views.music_status, name='music_status'),
    path('poseidon/', views.poseidon, name='poseidon'),
    path('api/poseidon/status/', views.api_poseidon_status, name='api_poseidon_status'),
    path('api/poseidon/ping-interno/', views.api_poseidon_ping_interno, name='api_poseidon_ping_interno'),
]
