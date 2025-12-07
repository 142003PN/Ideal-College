from django import forms
from .models import Results

class ResultsForm(forms.ModelForm):
    class Meta:
        model=Results
        