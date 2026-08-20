from django import forms
from django.utils import timezone
from .models import Opportunity


class OpportunityForm(forms.ModelForm):
    application_deadline = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text='Last date for students to submit applications'
    )

    class Meta:
        model = Opportunity
        fields = [
            'title', 'opportunity_type', 'job_role', 'description',
            'responsibilities', 'requirements', 'required_skills',
            'location', 'work_mode', 'stipend', 'salary', 'duration',
            'min_cgpa', 'eligible_degree', 'eligible_department',
            'graduation_year', 'application_deadline', 'openings_count'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full Stack Python Developer Intern'}),
            'opportunity_type': forms.Select(attrs={'class': 'form-select'}),
            'job_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineer / Data Analyst'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Overview of the role, team, and day-to-day work...'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Key responsibilities and deliverables...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Candidate qualifications, background, experience...'}),
            'required_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, PostgreSQL, REST API, Git'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangalore, Karnataka (or Remote)'}),
            'work_mode': forms.Select(attrs={'class': 'form-select'}),
            'stipend': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ₹30,000 / month (for internships)'}),
            'salary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ₹8,00,000 - ₹12,00,000 PA (for full-time)'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 6 Months / Full-time'}),
            'min_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00 for no cutoff, or e.g. 7.50'}),
            'eligible_degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B.Tech, M.Tech, MCA, B.Sc or All Degrees'}),
            'eligible_department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science, IT, Electronics or All Departments'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025 (or leave empty for any batch)'}),
            'openings_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
        }

    def clean_application_deadline(self):
        deadline = self.cleaned_data.get('application_deadline')
        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError("Application deadline cannot be in the past.")
        return deadline
