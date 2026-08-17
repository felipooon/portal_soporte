from django.contrib import admin
from .models import PersonalSoporte, ClienteCentro, Bitacora, EnlaceDocumentacion

admin.site.register(PersonalSoporte)
admin.site.register(ClienteCentro)
admin.site.register(Bitacora)
admin.site.register(EnlaceDocumentacion)
