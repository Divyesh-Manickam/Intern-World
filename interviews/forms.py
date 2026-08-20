from django import forms
from django.utils import timezone
from .models import Interview


class ScheduleInterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'interview_date', 'interview_time', 'interview_type',
            'meeting_link', 'location', 'instructions'
        ]
        widgets = {
            'interview_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'interview_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'interview_type': forms.Select(attrs={'class': 'form-select'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/... (if online)'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Office Address or Room Number (if offline)'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Preparation guidelines, topics, required documents...'}),
        }

    def clean_interview_date(self):
        date = self.cleaned_data.get('interview_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Interview date cannot be in the past.")
        return date
