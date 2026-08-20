from django.db import models
from django.conf import settings
from django.utils import timezone
from recruiters.models import Company


class Opportunity(models.Model):
    class OpportunityType(models.TextChoices):
        INTERNSHIP = 'INTERNSHIP', 'Internship'
        PLACEMENT = 'PLACEMENT', 'Full-Time Placement'

    class WorkMode(models.TextChoices):
        REMOTE = 'REMOTE', 'Remote'
        ON_SITE = 'ON_SITE', 'On-Site'
        HYBRID = 'HYBRID', 'Hybrid'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        CLOSED = 'CLOSED', 'Closed'
        REJECTED = 'REJECTED', 'Rejected'

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_opportunities'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='opportunities'
    )
    title = models.CharField(max_length=255)
    opportunity_type = models.CharField(
        max_length=20,
        choices=OpportunityType.choices,
        default=OpportunityType.INTERNSHIP
    )
    job_role = models.CharField(max_length=150)
    description = models.TextField()
    responsibilities = models.TextField(blank=True, default='')
    requirements = models.TextField(blank=True, default='')
    required_skills = models.TextField(
        help_text='Comma-separated skills (e.g. Python, Django, React, SQL)'
    )
    location = models.CharField(max_length=150)
    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.ON_SITE
    )
    stipend = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='e.g. ₹25,000 / month (or Unpaid / Performance based)'
    )
    salary = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='e.g. ₹6 - 10 LPA'
    )
    duration = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='e.g. 3 Months, 6 Months, Permanent'
    )
    min_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.0,
        help_text='Minimum CGPA cutoff (e.g. 7.00, 0 for no cutoff)'
    )
    eligible_degree = models.CharField(
        max_length=255,
        default='All Degrees',
        help_text='e.g. B.Tech, M.Tech, BCA, MCA, B.Sc or All Degrees'
    )
    eligible_department = models.CharField(
        max_length=255,
        default='All Departments',
        help_text='e.g. Computer Science, Information Technology, ECE or All Departments'
    )
    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Target graduating batch year (e.g. 2025, 2026, or blank for any)'
    )
    application_deadline = models.DateField()
    openings_count = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
        indexes = [
            models.Index(fields=['status', 'opportunity_type']),
            models.Index(fields=['location', 'work_mode']),
            models.Index(fields=['application_deadline']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company.name} ({self.get_opportunity_type_display()})"

    @property
    def is_active(self):
        return self.status == self.Status.APPROVED and self.application_deadline >= timezone.now().date()

    @property
    def skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    @property
    def is_expired(self):
        return self.application_deadline < timezone.now().date()


class SavedOpportunity(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_opportunities'
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='saved_by_students'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('student', 'opportunity')
        verbose_name = 'Saved Opportunity'
        verbose_name_plural = 'Saved Opportunities'

    def __str__(self):
        return f"{self.student.get_full_name()} saved {self.opportunity.title}"
