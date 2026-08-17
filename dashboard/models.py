from django.db import models

class PersonalSoporte(models.Model):
    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100, default='ASISTENTE DE SOPORTE')
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Personal de Soporte'
        verbose_name_plural = 'Personal de Soporte'


class ClienteCentro(models.Model):
    nombre = models.CharField(max_length=200)
    correo = models.EmailField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    class Meta:
        verbose_name = 'Cliente / Centro'
        verbose_name_plural = 'Clientes / Centros'

class Bitacora(models.Model):
    texto = models.TextField(blank=True, default='')
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bitácora de Turno (Actualizada: {self.actualizado_en.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        verbose_name = 'Bitácora de Turno'
        verbose_name_plural = 'Bitácoras de Turno'

class EnlaceDocumentacion(models.Model):
    titulo = models.CharField(max_length=100)
    url = models.URLField()
    icono = models.CharField(max_length=50, default='📘', help_text="Ej: 📘, 🔗, ⚙️")
    orden = models.IntegerField(default=0)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Enlace de Documentación'
        verbose_name_plural = 'Enlaces de Documentación'
        ordering = ['orden']
