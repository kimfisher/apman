from django import forms
from django.forms import ModelForm

from .models import SatelliteAudio


class SatelliteAudioForm(ModelForm):
    type = forms.ChoiceField(choices=SatelliteAudio.TYPES, widget=forms.RadioSelect)

    class Meta:
        model = SatelliteAudio
        exclude = ['satellite', 'user', 'reviewed', ]
