from django import forms
from .models import Staff, StaffProfile

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'NRC','email']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'NRC': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'First Name', 
            'last_name': 'Last Name',
            'NRC': 'NRC',
            'email': 'Email Address',
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['position', 'profile_picture', 'gender', 'department', 'employment_status', 'phone_number', 'address']

        widgets = {
            'position':forms.Select(attrs={'class':'form-control'}),
            'profile_picture':forms.ClearableFileInput(attrs={'class':'form-control'}),
            'gender':forms.Select(attrs={'class':'form-control'}),
            'department':forms.Select(attrs={'class':'form-control'}),
            'employment_status':forms.Select(attrs={'class':'form-control'}),
            'phone_number':forms.TextInput(attrs={'class':'form-control'}),
            'address':forms.Textarea(attrs={'class':'form-control', 'rows':3, 'cols':15}),
        }