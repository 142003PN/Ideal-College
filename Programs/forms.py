from django import forms
from .models import Programs
class ProgramForm(forms.ModelForm):
    class Meta:
        model = Programs
        fields = ['program_title', 'department_id']

        widgets = {
            'program_title': forms.TextInput(attrs={'class':'form-control'}),
            'department_id': forms.Select(attrs={'class':'form-control'})
        }