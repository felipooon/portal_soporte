from django.contrib import admin
from .models import PersonalSoporte, Empresa, Bitacora, Destinatario

@admin.register(PersonalSoporte)
class PersonalSoporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cargo', 'telefono', 'correo')

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    search_fields = ('nombre',)

@admin.register(Destinatario)
class DestinatarioAdmin(admin.ModelAdmin):
    list_display = ('correo', 'empresa', 'activo')
    list_filter = ('empresa', 'activo')
    search_fields = ('correo', 'empresa__nombre')

admin.site.register(Bitacora)
