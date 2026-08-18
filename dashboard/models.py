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


class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    correos = models.TextField(help_text="Correos separados por punto y coma (;) o comas (,)")
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({len(self.correos.split(','))} correos)"

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

class Bitacora(models.Model):
    texto = models.TextField(blank=True, default='')
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bitácora de Turno (Actualizada: {self.actualizado_en.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        verbose_name = 'Bitácora de Turno'
        verbose_name_plural = 'Bitácoras de Turno'

