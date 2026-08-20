from django import forms
from .models import Company, RecruiterProfile
from applications.models import Application


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'description', 'website', 'industry', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'About company, culture, perks...'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://company.com'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Technology, Healthcare, Finance'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Headquarters / Main Office'}),
        }


class RecruiterProfileForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = ['designation', 'department']
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Senior Talent Acquisition Specialist'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Human Resources'}),
        }


class ApplicantStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'recruiter_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'recruiter_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Private recruiter feedback / evaluation'}),
        }
