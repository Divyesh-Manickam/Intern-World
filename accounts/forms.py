from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User
from students.models import StudentProfile
from recruiters.models import Company, RecruiterProfile


class StudentRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))

    # Student Profile fields
    college = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. National Institute of Technology'}))
    degree = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B.Tech / B.E / MCA'}))
    department = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science and Engineering'}))
    graduation_year = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2025'}))
    cgpa = forms.DecimalField(max_digits=4, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8.50', 'step': '0.01'}))
    skills = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, React, SQL, Git'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.role = User.Role.STUDENT
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                college=self.cleaned_data.get('college'),
                degree=self.cleaned_data.get('degree'),
                department=self.cleaned_data.get('department'),
                graduation_year=self.cleaned_data.get('graduation_year'),
                cgpa=self.cleaned_data.get('cgpa'),
                skills=self.cleaned_data.get('skills'),
            )
        return user


class RecruiterRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'work@company.com'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))

    # Company & Recruiter fields
    company_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Acme Innovations'}))
    company_description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of company products/services'}))
    company_website = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://acme.com'}))
    industry = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Information Technology / Fintech'}))
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangalore, India'}))
    designation = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lead Talent Acquisition Specialist'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.role = User.Role.RECRUITER
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            company_name = self.cleaned_data.get('company_name')
            company, _ = Company.objects.get_or_create(
                name=company_name,
                defaults={
                    'description': self.cleaned_data.get('company_description', ''),
                    'website': self.cleaned_data.get('company_website', ''),
                    'industry': self.cleaned_data.get('industry', 'Technology'),
                    'location': self.cleaned_data.get('location', ''),
                    'verification_status': Company.VerificationStatus.PENDING,
                }
            )
            RecruiterProfile.objects.create(
                user=user,
                company=company,
                designation=self.cleaned_data.get('designation', 'Recruiter'),
            )
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your registered email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Check user by email
            try:
                user_obj = User.objects.get(email__iexact=email)
                user = authenticate(username=user_obj.email, password=password)
                if not user:
                    user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

            if not user:
                raise ValidationError("Invalid email or password. Please check your credentials.")
            if not user.is_active:
                raise ValidationError("This account has been deactivated. Please contact administrator.")

            self.user = user

        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
