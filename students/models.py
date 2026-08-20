from django.db import models
from django.conf import settings
from .services import validate_pdf_resume, calculate_profile_completion


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    college = models.CharField(max_length=255, default='', blank=True)
    degree = models.CharField(max_length=100, default='B.Tech', blank=True)
    department = models.CharField(max_length=150, default='Computer Science', blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.0, blank=True)
    
    # Skills
    skills = models.TextField(
        blank=True,
        default='',
        help_text='Comma-separated technical skills (e.g., Python, Django, React, SQL)'
    )
    soft_skills = models.TextField(
        blank=True,
        default='',
        help_text='Comma-separated soft skills (e.g., Leadership, Communication)'
    )
    bio = models.TextField(blank=True, default='')

    # Career Preferences
    preferred_location = models.CharField(max_length=200, blank=True, default='')
    preferred_role = models.CharField(max_length=200, blank=True, default='')

    # Resume File
    resume = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[validate_pdf_resume]
    )
    resume_extracted_text = models.TextField(blank=True, default='')

    # Links
    github_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    portfolio_url = models.URLField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email} ({self.college})"

    @property
    def skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def completion_percentage(self):
        return calculate_profile_completion(self)


class Project(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    technologies = models.CharField(max_length=255, help_text='Comma-separated technologies used')
    project_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"


class Certification(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.issuing_organization})"


class Experience(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date', '-created_at']

    def __str__(self):
        return f"{self.role} at {self.company}"
