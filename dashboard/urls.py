from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('correos-masivos/', views.correos_masivos, name='correos_masivos'),
    path('certificados/', views.certificados, name='certificados'),
    path('calendario/', views.calendario, name='calendario'),
]
