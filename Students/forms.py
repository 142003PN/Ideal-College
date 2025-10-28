from django import forms
from .models import StudentProfile, Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'NRC','email', 'password']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'NRC': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password':forms.PasswordInput(attrs={'class': 'form-control'})
        }
        labels = {
            'first_name': 'First Name', 
            'last_name': 'Last Name',
            'NRC': 'NRC',
            'email': 'Email Address',
            'password':'Password'
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['program','profile_picture', 
                  'gender', 'date_of_birth', 'address', 'phone_number', 'year_of_study']
        
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control','placeholder':'2001-12-31'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.Select(attrs={'class': 'form-control'}),

        }
        labels = {
            'program': 'Program',
            'profile_picture': 'Profile Picture',
            'gender': 'Gender',
            'date_of_birth': 'Date of Birth',   
            'address': 'Address',
            'phone_number': 'Phone Number',
            'year_of_study': 'Year of Study',
        }
    