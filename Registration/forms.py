from django import forms 
from .models import *
class Registration_Form(forms.ModelForm):
    class Meta:
        model = Registration
        fields=['student_id', 'courses', 'year_of_study']

        widgets={
            'student_id':forms.NumberInput(attrs={'class':'form-control'}),
            'courses':forms.CheckboxSelectMultiple(attrs={'class':'check-input'}),
            'year_of_study':forms.CheckboxInput()
        }