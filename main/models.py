from django.conf import settings
from django.db import models

# Create your models here.

class Perfil(models.Model):
    nombre = models.CharField(max_length=30)
    dni = models.CharField(max_length=9)
    fecha_nac = models.DateField()
    direccion = models.CharField(max_length=30)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)

    def __str__(self):
        return str(self.nombre)

class Sala(models.Model):
    nombre = models.CharField(max_length=10)
    mapa = models.ImageField(upload_to='main/imagenes/')
    aforo = models.IntegerField()

    def __str__(self):
        return 'Id: %s Nombre: %s Mapa: %s Aforo: %s' % (self.id, self.nombre, self.mapa, self.aforo)


class Zona(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.RESTRICT)
    nombre = models.CharField(max_length=10)
    aforo = models.IntegerField()

    def __str__(self):
        return 'Sala: %s Nombre: %s Id: %s Aforo: %s' % (self.sala, self.nombre, self.id, self.aforo)

class Asiento(models.Model):
    zona = models.ForeignKey(Zona, on_delete=models.RESTRICT)
    nombre = models.CharField(max_length=10)

    def __str__(self):
        return 'Zona: %s Nombre: %s Id: %s' % (self.zona, self.nombre, self.id)

class Evento(models.Model):
    nombre = models.CharField(max_length=10)
    imagen = models.ImageField(upload_to='main/imagenes/')
    fecha_hora = models.DateTimeField()
    disponibles = models.IntegerField()
    sala = models.ForeignKey(Sala, on_delete=models.RESTRICT)

    def __str__(self):
        return 'ID: %s Nombre: %s Fecha: %s' % (self.id, self.nombre, self.fecha_hora)

class Zona_evento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.RESTRICT)
    zona = models.ForeignKey(Zona, on_delete=models.RESTRICT)
    disponibles = models.IntegerField()
    precio = models.FloatField()

    def __str__(self):
        return 'ID: %s Zona: %s Evento: %s Disponibles: %s Precio: %s' % (self.id, self.zona, self.evento, self.disponibles, self.precio)

class Asiento_evento(models.Model):
    zona_evento = models.ForeignKey(Zona_evento, on_delete=models.RESTRICT)
    asiento = models.ForeignKey(Asiento, on_delete=models.RESTRICT)
    estado = models.BooleanField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True)

    def __str__(self):
        return 'ID: %s Zona: %s Asiento: %s' % (self.id, self.zona_evento, self.asiento)


class Compra_total(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True)
    fecha_hora = models.DateTimeField()
    zona_evento = models.ForeignKey(Zona_evento, on_delete=models.RESTRICT)
    total = models.FloatField()

    def __str__(self):
        return 'ID: %s usuario: %s fecha_hora: %s zona_evento: %s total: %s' % (self.id, self.usuario, self.fecha_hora, self.zona_evento, self.total)
class Compra_asiento(models.Model):
    asiento_evento = models.ForeignKey(Asiento_evento, on_delete=models.RESTRICT)
    compra = models.ForeignKey(Compra_total, on_delete=models.RESTRICT)

    def __str__(self):
        return 'ID: %s Asiento: %s Compra: %s' % (self.id, self.asiento_evento, self.compra)