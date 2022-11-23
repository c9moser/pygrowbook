from django import forms
from django.utils.translation import gettext_lazy as _
from main.functions import get_supported_languages
from main.config import get_locale

class BreederForm(forms.Form):
    primary_key = forms.IntegerField(widget=forms.HiddenInput(),
                                     required=True)
    name = forms.CharField(label=_("Breeder Name:"),
                           max_length=128,
                           required=True)
    key = forms.SlugField(label=_("Breeder Key:"),
                          max_length=64,
                          required=True)
    homepage = forms.URLField(label=_('Homepage:'),
                              max_length=512,
                              required=False)
    seedfinder = forms.URLField(label=_('Seedfinder.eu:'),
                                max_length=512,
                                required=False)
# BreederForm class
                                
class StrainForm(forms.Form):
    primary_key = forms.IntegerField(widget=forms.HiddenInput(),
                                     required=True)
    breeder_key = forms.SlugField(widget=forms.HiddenInput(),
                                  max_length=64,
                                  required=True)
    name = forms.CharField(label=_('Strain Name:'),
                           max_length=128,
                           required=True)
    key = forms.SlugField(label=_('Strain Key:'),
                          max_length=64,
                          required=True)
    homepage = forms.URLField(label=_('Homepage:'),
                              max_length=512,
                              required=False)
    seedfinder = forms.URLField(label=_('Seedfinder.eu:'),
                                max_length=512,
                                required=False)
    info = forms.CharField(widget=forms.Textarea(),
                           label=_('Info:'),
                           required=False)
    description = forms.CharField(widget=forms.Textarea(),  
                                  label=_('Description'),
                                  required=False)
# StrainForm class
                                  
class StrainTranslationForm(forms.Form):
    breeder_key = forms.CharField(widget=forms.HiddenInput(),
                                  max_length=64,
                                  required=True)
    strain_key = forms.CharField(widget=forms.HiddenInput(),
                                 max_length=64,
                                 required=True)
    strain_id = forms.IntegerField(widget=forms.HiddenInput(),
                                   required=True)
    language = forms.CharField(widget=forms.HiddenInput(),required=True)
    homepage = forms.URLField(label=_('Homepage:'),
                                      max_length=512,
                                      required=False)
    seedfinder = forms.URLField(label=_('Seedfinder.eu'),
                                max_length=512,
                                required=False)
    info = forms.CharField(widget=forms.Textarea(),
                           label=_('Info:'),
                           required=False)
    description = forms.CharField(widget=forms.Textarea(),
                                  label=_('Description:'),
                                  required=False)
                            
    def __init__(self,*args,**kwargs):
        super(StrainTranslationForm,self).__init__(*args,**kwargs)
# StrainTranslationForm class
