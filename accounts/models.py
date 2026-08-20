from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        RECRUITER = 'RECRUITER', 'Recruiter'
        ADMIN = 'ADMIN', 'Administrator'

    email = models.EmailField(unique=True, verbose_name='Email Address')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text='Designates the role of this user on the platform.'
    )
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone Number')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_recruiter(self):
        return self.role == self.Role.RECRUITER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser or self.is_staff
