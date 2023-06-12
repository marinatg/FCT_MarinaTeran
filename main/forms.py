from django import forms
from django.forms import ModelForm
from .models import *

class UnidadesForm(forms.Form):
    unidades = forms.IntegerField(required=True, min_value=1)

class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = '__all__'

class ZonaForm(forms.ModelForm):
    class Meta:
        model = Zona
        fields = '__all__'

class AsientoForm(forms.ModelForm):
    class Meta:
        model = Asiento
        fields = '__all__'

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'imagen', 'fecha_hora', 'sala']


