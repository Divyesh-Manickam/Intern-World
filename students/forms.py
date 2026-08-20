from django import forms
from .models import StudentProfile, Project, Certification, Experience
from .services import validate_pdf_resume


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'college', 'degree', 'department', 'graduation_year', 'cgpa',
            'skills', 'soft_skills', 'bio', 'preferred_location', 'preferred_role',
            'github_url', 'linkedin_url', 'portfolio_url'
        ]
        widgets = {
            'college': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. National Institute of Technology'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B.Tech, MCA'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science and Engineering'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2025'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '8.50'}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, React, PostgreSQL, Docker'}),
            'soft_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Communication, Team Collaboration, Problem Solving'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief summary of your background, goals, and passions...'}),
            'preferred_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bangalore, Hyderabad, Remote'}),
            'preferred_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Software Engineer, Full Stack Developer'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/yourhandle'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourhandle'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourportfolio.com'}),
        }


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,application/pdf'})
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            validate_pdf_resume(resume)
        return resume


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'project_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe features, problem solved, impact...'}),
            'technologies': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Django, Vue.js, PostgreSQL, Redis'}),
            'project_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/project-repo'}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'issue_date', 'credential_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AWS Certified Solutions Architect'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Amazon Web Services'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.credly.com/...'}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'role', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Development Intern'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key responsibilities and achievements...'}),
        }
