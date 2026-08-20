from django.contrib import admin
from .models import Company, RecruiterProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'location', 'verification_status', 'verified_at', 'created_at')
    list_filter = ('verification_status', 'industry')
    search_fields = ('name', 'location', 'industry')
    prepopulated_fields = {'slug': ('name',)}
    actions = ['verify_companies', 'reject_companies']

    def verify_companies(self, request, queryset):
        queryset.update(verification_status=Company.VerificationStatus.VERIFIED)
    verify_companies.short_description = "Mark selected companies as Verified"

    def reject_companies(self, request, queryset):
        queryset.update(verification_status=Company.VerificationStatus.REJECTED)
    reject_companies.short_description = "Mark selected companies as Rejected"


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'designation', 'department', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company__name')
