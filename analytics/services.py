from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from collections import Counter

from accounts.models import User
from recruiters.models import Company
from opportunities.models import Opportunity
from applications.models import Application
from interviews.models import Interview


def get_platform_overview_stats():
    """
    Returns platform-wide summary statistics for administrators.
    """
    total_students = User.objects.filter(role=User.Role.STUDENT).count()
    total_recruiters = User.objects.filter(role=User.Role.RECRUITER).count()
    total_companies = Company.objects.count()
    verified_companies = Company.objects.filter(verification_status=Company.VerificationStatus.VERIFIED).count()
    pending_companies = Company.objects.filter(verification_status=Company.VerificationStatus.PENDING).count()

    total_opportunities = Opportunity.objects.count()
    active_internships = Opportunity.objects.filter(
        opportunity_type=Opportunity.OpportunityType.INTERNSHIP,
        status=Opportunity.Status.APPROVED
    ).count()
    active_placements = Opportunity.objects.filter(
        opportunity_type=Opportunity.OpportunityType.PLACEMENT,
        status=Opportunity.Status.APPROVED
    ).count()
    pending_opportunities = Opportunity.objects.filter(status=Opportunity.Status.PENDING).count()

    total_applications = Application.objects.count()
    selected_candidates = Application.objects.filter(status=Application.Status.SELECTED).count()
    interviews_scheduled = Interview.objects.filter(status=Interview.Status.SCHEDULED).count()

    selection_rate = 0
    if total_applications > 0:
        selection_rate = round((selected_candidates / total_applications) * 100, 1)

    return {
        'total_students': total_students,
        'total_recruiters': total_recruiters,
        'total_companies': total_companies,
        'verified_companies': verified_companies,
        'pending_companies': pending_companies,
        'total_opportunities': total_opportunities,
        'active_internships': active_internships,
        'active_placements': active_placements,
        'pending_opportunities': pending_opportunities,
        'total_applications': total_applications,
        'selected_candidates': selected_candidates,
        'interviews_scheduled': interviews_scheduled,
        'selection_rate': selection_rate,
    }


def get_recruiter_dashboard_stats(recruiter_user):
    """
    Returns statistics specific to a recruiter user.
    """
    opps = Opportunity.objects.filter(recruiter=recruiter_user)
    total_opps = opps.count()
    active_opps = opps.filter(status=Opportunity.Status.APPROVED).count()
    
    apps = Application.objects.filter(opportunity__recruiter=recruiter_user)
    total_apps = apps.count()
    shortlisted = apps.filter(status=Application.Status.SHORTLISTED).count()
    interviews = Interview.objects.filter(recruiter=recruiter_user).count()
    selected = apps.filter(status=Application.Status.SELECTED).count()
    under_review = apps.filter(status=Application.Status.UNDER_REVIEW).count()

    return {
        'total_opps': total_opps,
        'active_opps': active_opps,
        'total_apps': total_apps,
        'under_review': under_review,
        'shortlisted': shortlisted,
        'interviews': interviews,
        'selected': selected,
    }


def get_monthly_applications_data():
    """
    Aggregates applications created per month for the last 6 months.
    """
    six_months_ago = timezone.now() - timedelta(days=180)
    qs = (
        Application.objects.filter(applied_at__gte=six_months_ago)
        .annotate(month=TruncMonth('applied_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = []
    counts = []
    for item in qs:
        if item['month']:
            labels.append(item['month'].strftime('%b %Y'))
            counts.append(item['count'])

    if not labels:
        # Fallback default empty months
        now = timezone.now()
        for i in range(5, -1, -1):
            m = now - timedelta(days=i*30)
            labels.append(m.strftime('%b %Y'))
            counts.append(0)

    return {'labels': labels, 'data': counts}


def get_application_funnel_data(recruiter_user=None):
    """
    Returns counts by application status for conversion funnel chart.
    """
    qs = Application.objects.all()
    if recruiter_user:
        qs = qs.filter(opportunity__recruiter=recruiter_user)

    statuses = [
        ('Applied', Application.Status.APPLIED),
        ('Under Review', Application.Status.UNDER_REVIEW),
        ('Shortlisted', Application.Status.SHORTLISTED),
        ('Interview', Application.Status.INTERVIEW_SCHEDULED),
        ('Selected', Application.Status.SELECTED),
        ('Rejected', Application.Status.REJECTED),
    ]

    labels = []
    data = []
    for label, code in statuses:
        labels.append(label)
        data.append(qs.filter(status=code).count())

    return {'labels': labels, 'data': data}


def get_popular_skills_data(limit=8):
    """
    Aggregates top required skills across opportunities.
    """
    skills_counter = Counter()
    for opp in Opportunity.objects.all():
        for s in opp.skills_list:
            skills_counter[s.title()] += 1

    top_skills = skills_counter.most_common(limit)
    labels = [k for k, v in top_skills]
    counts = [v for k, v in top_skills]

    return {'labels': labels, 'data': counts}


def get_active_companies_data(limit=5):
    """
    Returns companies with highest number of posted opportunities.
    """
    qs = (
        Company.objects.annotate(job_count=Count('opportunities'))
        .order_by('-job_count')[:limit]
    )
    labels = [c.name for c in qs]
    counts = [c.job_count for c in qs]
    company_items = [{'name': c.name, 'count': c.job_count} for c in qs]

    return {'labels': labels, 'data': counts, 'items': company_items}
