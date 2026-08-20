from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Company(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Verification'
        VERIFIED = 'VERIFIED', 'Verified'
        REJECTED = 'REJECTED', 'Rejected'

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    industry = models.CharField(max_length=100, blank=True, default='Technology')
    location = models.CharField(max_length=255, blank=True, default='')
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            count = 1
            while Company.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_verification_status_display()})"

    @property
    def is_verified(self):
        return self.verification_status == self.VerificationStatus.VERIFIED


class RecruiterProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruiter_profile'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recruiters'
    )
    designation = models.CharField(max_length=150, blank=True, default='Talent Acquisition')
    department = models.CharField(max_length=150, blank=True, default='Human Resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Recruiter Profile'
        verbose_name_plural = 'Recruiter Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name if self.company else 'No Company'}"
