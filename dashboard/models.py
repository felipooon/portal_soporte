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
