from django import forms
from .models import Application
from students.services import validate_pdf_resume


class ApplicationSubmitForm(forms.ModelForm):
    resume = forms.FileField(
        required=False,
        validators=[validate_pdf_resume],
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,application/pdf'})
    )

    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Introduce yourself, why you are a great fit, and your relevant projects...'}
            ),
        }
