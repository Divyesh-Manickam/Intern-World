from django.contrib import admin
from .models import StudentProfile, Project, Certification, Experience


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'degree', 'department', 'graduation_year', 'cgpa', 'completion_percentage', 'created_at')
    list_filter = ('degree', 'department', 'graduation_year')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'college', 'skills')
    inlines = [ProjectInline, CertificationInline, ExperienceInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'technologies', 'created_at')
    search_fields = ('title', 'technologies', 'student__user__email')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'issuing_organization', 'issue_date')
    search_fields = ('name', 'issuing_organization', 'student__user__email')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('role', 'company', 'student', 'start_date', 'end_date', 'is_current')
    search_fields = ('company', 'role', 'student__user__email')
