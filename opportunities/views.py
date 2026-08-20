from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone

from accounts.decorators import recruiter_required
from accounts.models import User
from recruiters.models import Company, RecruiterProfile
from .models import Opportunity, SavedOpportunity
from .forms import OpportunityForm
from .filters import OpportunityFilter
from applications.models import Application
from recommendations.services import calculate_opportunity_match
from notifications.services import create_notification
from notifications.models import Notification


def landing_page(request):
    """
    Public home page featuring platform highlights, top opportunities, companies, and stats.
    """
    popular_opportunities = Opportunity.objects.filter(
        status=Opportunity.Status.APPROVED,
        application_deadline__gte=timezone.now().date()
    ).select_related('company')[:6]

    top_companies = Company.objects.filter(
        verification_status=Company.VerificationStatus.VERIFIED
    ).annotate(job_count=Count('opportunities'))[:6]

    stats = {
        'total_students': User.objects.filter(role=User.Role.STUDENT).count(),
        'total_companies': Company.objects.count(),
        'total_jobs': Opportunity.objects.filter(status=Opportunity.Status.APPROVED).count(),
        'total_selections': Application.objects.filter(status=Application.Status.SELECTED).count(),
    }

    # If student is logged in, fetch their saved opportunities
    saved_ids = []
    if request.user.is_authenticated and request.user.is_student:
        saved_ids = list(SavedOpportunity.objects.filter(student=request.user).values_list('opportunity_id', flat=True))

    context = {
        'popular_opportunities': popular_opportunities,
        'top_companies': top_companies,
        'stats': stats,
        'saved_ids': saved_ids,
    }
    return render(request, 'landing.html', context)


def about_page(request):
    """
    Public About Page for InternWorld.
    """
    return render(request, 'about.html')


def opportunity_list(request):
    """
    Public and student opportunity discovery catalog.
    Supports filtering, keyword search, sorting, pagination, and compatibility score badges.
    """
    queryset = Opportunity.objects.filter(
        status=Opportunity.Status.APPROVED,
        application_deadline__gte=timezone.now().date()
    ).select_related('company', 'recruiter').order_by('-created_at')

    filter_set = OpportunityFilter(request.GET, queryset=queryset)
    filtered_qs = filter_set.qs

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'created_at', 'application_deadline', '-openings_count']:
        filtered_qs = filtered_qs.order_by(sort_by)

    # Attach match score if student is logged in
    student_profile = None
    saved_ids = []
    if request.user.is_authenticated and request.user.is_student:
        student_profile = getattr(request.user, 'student_profile', None)
        saved_ids = list(SavedOpportunity.objects.filter(student=request.user).values_list('opportunity_id', flat=True))

    # Pagination
    paginator = Paginator(filtered_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Attach match score to items in current page
    for opp in page_obj:
        if student_profile:
            opp.match_breakdown = calculate_opportunity_match(student_profile, opp)
        else:
            opp.match_breakdown = None

    context = {
        'filter': filter_set,
        'page_obj': page_obj,
        'saved_ids': saved_ids,
        'total_count': filtered_qs.count(),
        'current_sort': sort_by,
    }
    return render(request, 'opportunities/list.html', context)


def opportunity_detail(request, pk):
    """
    Comprehensive view of a specific opportunity.
    """
    opportunity = get_object_or_404(
        Opportunity.objects.select_related('company', 'recruiter'),
        pk=pk
    )

    # Increment view count
    Opportunity.objects.filter(pk=pk).update(views_count=opportunity.views_count + 1)

    existing_application = None
    is_saved = False
    match_breakdown = None

    if request.user.is_authenticated:
        if request.user.is_student:
            student_profile = getattr(request.user, 'student_profile', None)
            existing_application = Application.objects.filter(student=request.user, opportunity=opportunity).first()
            is_saved = SavedOpportunity.objects.filter(student=request.user, opportunity=opportunity).exists()
            if student_profile:
                match_breakdown = calculate_opportunity_match(student_profile, opportunity)

    # Related opportunities from same company or role
    related_opportunities = Opportunity.objects.filter(
        status=Opportunity.Status.APPROVED,
        application_deadline__gte=timezone.now().date()
    ).exclude(pk=pk).filter(
        Q(company=opportunity.company) | Q(job_role__icontains=opportunity.job_role)
    )[:3]

    context = {
        'opportunity': opportunity,
        'existing_application': existing_application,
        'is_saved': is_saved,
        'match_breakdown': match_breakdown,
        'related_opportunities': related_opportunities,
    }
    return render(request, 'opportunities/detail.html', context)


@login_required
@recruiter_required
def create_opportunity(request):
    """
    Recruiter creates a new internship or placement opportunity.
    """
    profile, _ = RecruiterProfile.objects.get_or_create(user=request.user)
    company = profile.company

    if not company:
        messages.warning(request, "Please set up your company profile before posting an opportunity.")
        return redirect('recruiters:edit_company')

    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.recruiter = request.user
            opportunity.company = company
            
            # If company is verified, auto-approve; else require admin review
            if company.is_verified:
                opportunity.status = Opportunity.Status.APPROVED
                messages.success(request, "Opportunity published successfully!")
            else:
                opportunity.status = Opportunity.Status.PENDING
                messages.info(
                    request,
                    "Opportunity submitted for review. Since your company profile is pending verification, "
                    "an administrator will review and approve this posting shortly."
                )

            opportunity.save()
            return redirect('opportunities:my_opportunities')
    else:
        form = OpportunityForm()

    return render(request, 'opportunities/create_opportunity.html', {'form': form, 'company': company})


@login_required
@recruiter_required
def edit_opportunity(request, pk):
    """
    Recruiter edits an existing opportunity.
    """
    opportunity = get_object_or_404(Opportunity, pk=pk, recruiter=request.user)

    if request.method == 'POST':
        form = OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            form.save()
            messages.success(request, f"Opportunity '{opportunity.title}' updated successfully.")
            return redirect('opportunities:my_opportunities')
    else:
        form = OpportunityForm(instance=opportunity)

    return render(request, 'opportunities/edit_opportunity.html', {'form': form, 'opportunity': opportunity})


@login_required
@recruiter_required
def close_opportunity(request, pk):
    """
    Recruiter closes an opportunity so no further applications are accepted.
    """
    opportunity = get_object_or_404(Opportunity, pk=pk, recruiter=request.user)
    opportunity.status = Opportunity.Status.CLOSED
    opportunity.save(update_fields=['status'])
    messages.info(request, f"Opportunity '{opportunity.title}' has been marked as Closed.")
    return redirect('opportunities:my_opportunities')


@login_required
@recruiter_required
def delete_opportunity(request, pk):
    """
    Recruiter deletes an opportunity.
    """
    opportunity = get_object_or_404(Opportunity, pk=pk, recruiter=request.user)
    opportunity.delete()
    messages.info(request, "Opportunity removed successfully.")
    return redirect('opportunities:my_opportunities')


@login_required
@recruiter_required
def my_opportunities(request):
    """
    Recruiter's posted opportunities list with application statistics.
    """
    opportunities = Opportunity.objects.filter(
        recruiter=request.user
    ).annotate(
        total_apps=Count('applications'),
        shortlisted_apps=Count('applications', filter=Q(applications__status=Application.Status.SHORTLISTED)),
        selected_apps=Count('applications', filter=Q(applications__status=Application.Status.SELECTED))
    ).order_by('-created_at')

    return render(request, 'opportunities/my_opportunities.html', {'opportunities': opportunities})
