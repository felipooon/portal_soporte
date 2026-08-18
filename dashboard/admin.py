from django.contrib import admin
from .models import PersonalSoporte, Empresa, Bitacora

@admin.register(PersonalSoporte)
class PersonalSoporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cargo', 'telefono', 'correo')

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    search_fields = ('nombre', 'correos')

admin.site.register(Bitacora)
