from django import forms
from .models import Courses
class CourseForm(forms.ModelForm):
    class Meta:
        model = Courses
        fields = ['course_code', 'course_title', 'program_id', 'year_of_study']

        widgets = {
            'course_code':forms.TextInput(attrs={'class':'form-control'}),
            'course_title':forms.TextInput(attrs={'class':'form-control'}),
            'program_id':forms.Select(attrs={'class':'form-control'}),
            'year_of_study':forms.Select(attrs={'class':'form-control'})
        }