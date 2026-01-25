from django import forms
from .models import *

class SessionYearForm(forms.ModelForm):
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        required=True,
        error_messages={
            'required':'Please Select Semester'
        },
        widget=forms.Select(attrs={'class':'form-control form-select',})
    )
    class Meta:
        model = SessionYear
        fields = ['year_title', 'intake','is_current_year', 'semester']
        widgets = {
            'year_title': forms.TextInput(attrs={'class': 'form-control'}),
            'intake': forms.Select(attrs={'class': 'form-control form-select'}),
            'is_current_year': forms.CheckboxInput(attrs={'class': 'form-check'}),
        }

class YearOfStudyForm(forms.ModelForm):
    class Meta:
        model = YearOfStudy
        fields = ['year_title']

        widgets={
            'year_title': forms.Select(attrs={'class': 'form-control form-select'}),
        }

#--------Semester Form-----------------
class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['semester_name']
        widgets = {
            'semester_name': forms.Select(attrs={'class': 'form-control form-select'}),
        }

 #---------Intake Form-----------------       
class IntakeForm(forms.ModelForm):
    class Meta:
        model = Intake
        fields = ['intake_name']

        widgets={
            'intake_name': forms.Select(attrs={'class': 'form-control form-select'}),
        }