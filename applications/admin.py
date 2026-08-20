from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'opportunity', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'opportunity__title', 'opportunity__company__name')
    actions = ['shortlist_applications', 'mark_selected', 'reject_applications']

    def shortlist_applications(self, request, queryset):
        queryset.update(status=Application.Status.SHORTLISTED)
    shortlist_applications.short_description = "Shortlist selected applications"

    def mark_selected(self, request, queryset):
        queryset.update(status=Application.Status.SELECTED)
    mark_selected.short_description = "Mark selected applications as Selected"

    def reject_applications(self, request, queryset):
        queryset.update(status=Application.Status.REJECTED)
    reject_applications.short_description = "Reject selected applications"
