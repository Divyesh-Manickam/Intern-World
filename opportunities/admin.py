from django.contrib import admin
from .models import Opportunity, SavedOpportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'opportunity_type', 'job_role', 'location', 'work_mode', 'status', 'application_deadline', 'created_at')
    list_filter = ('opportunity_type', 'work_mode', 'status', 'created_at')
    search_fields = ('title', 'company__name', 'job_role', 'required_skills', 'location')
    actions = ['approve_opportunities', 'reject_opportunities', 'close_opportunities']

    def approve_opportunities(self, request, queryset):
        queryset.update(status=Opportunity.Status.APPROVED)
    approve_opportunities.short_description = "Approve selected opportunities"

    def reject_opportunities(self, request, queryset):
        queryset.update(status=Opportunity.Status.REJECTED)
    reject_opportunities.short_description = "Reject selected opportunities"

    def close_opportunities(self, request, queryset):
        queryset.update(status=Opportunity.Status.CLOSED)
    close_opportunities.short_description = "Close selected opportunities"


@admin.register(SavedOpportunity)
class SavedOpportunityAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'created_at')
    search_fields = ('student__email', 'opportunity__title')
