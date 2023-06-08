from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Perfil)
admin.site.register(Sala)
admin.site.register(Zona)
admin.site.register(Asiento)
admin.site.register(Evento)
admin.site.register(Zona_evento)
admin.site.register(Asiento_evento)
admin.site.register(Compra_asiento)
admin.site.register(Compra_total)