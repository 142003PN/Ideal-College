from django import forms
from .models import SessionYear
from Courses.models import YearOfStudy

class SessionYearForm(forms.ModelForm):
    class Meta:
        model = SessionYear
        fields = ['year_title', 'is_current_year']
        widgets = {
            'year_title': forms.TextInput(attrs={'class': 'form-control'}),
            'is_current_year': forms.CheckboxInput(attrs={'class': 'form-check'}),
        }

class YearOfStudyForm(forms.ModelForm):
    class Meta:
        model = YearOfStudy
        fields = ['year_title']

        widgets={
            'year_title': forms.TextInput(attrs={'class': 'form-control'}),
        }