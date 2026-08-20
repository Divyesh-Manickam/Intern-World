import django_filters
from django import forms
from django.db.models import Q
from .models import Opportunity


class OpportunityFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    opportunity_type = django_filters.ChoiceFilter(
        choices=Opportunity.OpportunityType.choices,
        empty_label='All Opportunity Types',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    work_mode = django_filters.ChoiceFilter(
        choices=Opportunity.WorkMode.choices,
        empty_label='All Work Modes',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City or Region'})
    )
    company = django_filters.CharFilter(
        field_name='company__name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'})
    )
    required_skills = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Skill (e.g. Python)'})
    )

    class Meta:
        model = Opportunity
        fields = ['opportunity_type', 'work_mode', 'location', 'company', 'required_skills']

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) |
            Q(job_role__icontains=value) |
            Q(company__name__icontains=value) |
            Q(required_skills__icontains=value) |
            Q(description__icontains=value) |
            Q(location__icontains=value)
        )
