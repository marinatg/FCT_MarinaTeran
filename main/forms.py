from django import forms
from django.forms import ModelForm
from .models import *

class UnidadesForm(forms.Form):
    unidades = forms.IntegerField(required=True, min_value=1)