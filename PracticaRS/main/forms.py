#encoding:utf-8
from django import forms
from main.models import Anime

class AnimeBusquedaForm(forms.Form):
    idAnime = forms.IntegerField(label="Id del Anime", widget=forms.TextInput, required=True)

class FormatoBusquedaForm(forms.Form):
    # El SpinBox (ChoiceField) se llena dinámicamente con los formatos de la BD
    formato = forms.ChoiceField(label="Seleccione Formato", choices=[])
    
    def __init__(self, *args, **kwargs):
        super(FormatoBusquedaForm, self).__init__(*args, **kwargs)
        # Obtenemos los formatos únicos de la BD
        formatos = Anime.objects.values_list('formato', flat=True).distinct().order_by('formato')
        # Creamos una lista de tuplas (valor, etiqueta)
        choices = [(f, f) for f in formatos if f] # Evitamos vacíos
        self.fields['formato'].choices = choices