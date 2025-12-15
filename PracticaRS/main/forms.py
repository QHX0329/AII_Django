from django import forms
from main.models import Anime

class CargaForm(forms.Form):
    pass

class FormatoEmisionForm(forms.Form):
    formato = forms.ChoiceField(label="Selecciona formato de emisión", choices=[])

    def __init__(self, *args, **kwargs):
        super(FormatoEmisionForm, self).__init__(*args, **kwargs)
        formatos = Anime.objects.values_list('formato_emision', flat=True).distinct().order_by('formato_emision')
        OPCIONES = [(f, f) for f in formatos if f]
        self.fields['formato'].choices = OPCIONES

class AnimeBusquedaForm(forms.Form):
    anime_id = forms.IntegerField(label="ID del Anime", required=True, min_value=1)