from typing import Text
from django import forms
from .models import formModel
from django.forms import TextInput, Select, ClearableFileInput

class uploadFileForm(forms.ModelForm):
    class Meta:
        model = formModel
        fields = ["file_name", "subject"]
        widgets = {
            'subject': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'placeholder': 'machine learning'
            }),

            'file_name': ClearableFileInput(attrs={
                'class': "form-control",
                'padding-left': '2px;',
            }),



        }
