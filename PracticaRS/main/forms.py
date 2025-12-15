# main/forms.py
#encoding:utf-8
from django import forms
from main.models import Anime

class CargaForm(forms.Form):
    # Formulario vacío para confirmación simple
    pass

class FormatoEmisionForm(forms.Form):
    # El queryset se llenará dinámicamente en la vista o __init__ si fuera ModelChoice, 
    # pero para un ChoiceField simple lo haremos en la vista o usaremos un ModelChoice
    # Para ser estrictos con Django, lo ideal es obtener los valores distintos.
    formato = forms.ChoiceField(label="Selecciona formato de emisión", choices=[])

    def __init__(self, *args, **kwargs):
        super(FormatoEmisionForm, self).__init__(*args, **kwargs)
        # Obtenemos los formatos únicos de la BD
        formatos = Anime.objects.values_list('formato_emision', flat=True).distinct().order_by('formato_emision')
        OPCIONES = [(f, f) for f in formatos if f] # Evitamos vacíos
        self.fields['formato'].choices = OPCIONES

class AnimeBusquedaForm(forms.Form):
    anime_id = forms.IntegerField(label="ID del Anime", required=True, min_value=1)