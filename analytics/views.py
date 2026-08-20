from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from accounts.decorators import admin_required
from accounts.models import User
from recruiters.models import Company
from opportunities.models import Opportunity
from applications.models import Application
from interviews.models import Interview
from notifications.services import create_notification
from notifications.models import Notification
from .services import (
    get_platform_overview_stats,
    get_monthly_applications_data,
    get_application_funnel_data,
    get_popular_skills_data,
    get_active_companies_data
)


@login_required
@admin_required
def admin_dashboard(request):
    """
    Main Administrator Dashboard.
    Displays platform statistics, verification queues, approval queues, and analytics charts.
    """
    stats = get_platform_overview_stats()
    
    # Pending queues
    pending_companies = Company.objects.filter(
        verification_status=Company.VerificationStatus.PENDING
    ).order_by('-created_at')[:5]

    pending_opportunities = Opportunity.objects.filter(
        status=Opportunity.Status.PENDING
    ).select_related('company', 'recruiter').order_by('-created_at')[:5]

    recent_applications = Application.objects.select_related(
        'student', 'opportunity__company'
    ).order_by('-applied_at')[:8]

    # Chart datasets
    monthly_apps = get_monthly_applications_data()
    funnel_data = get_application_funnel_data()
    popular_skills = get_popular_skills_data(8)
    top_companies = get_active_companies_data(5)

    context = {
        'stats': stats,
        'pending_companies': pending_companies,
        'pending_opportunities': pending_opportunities,
        'recent_applications': recent_applications,
        'monthly_apps': monthly_apps,
        'funnel_data': funnel_data,
        'popular_skills': popular_skills,
        'top_companies': top_companies,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
@admin_required
def admin_manage_users(request):
    """
    Admin user management for students and recruiters.
    """
    role_filter = request.GET.get('role')
    search = request.GET.get('search')

    users = User.objects.exclude(is_superuser=True).order_by('-date_joined')

    if role_filter in [User.Role.STUDENT, User.Role.RECRUITER]:
        users = users.filter(role=role_filter)

    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search)
        )

    context = {
        'users': users,
        'selected_role': role_filter,
        'search': search,
    }
    return render(request, 'admin_dashboard/manage_users.html', context)


@login_required
@admin_required
def admin_toggle_user_status(request, pk):
    """
    Activate/Deactivate a user account.
    """
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj.is_superuser:
        messages.error(request, "Cannot alter superuser status from here.")
        return redirect('analytics:admin_users')

    user_obj.is_active = not user_obj.is_active
    user_obj.save(update_fields=['is_active'])
    status_str = "activated" if user_obj.is_active else "deactivated"
    messages.success(request, f"User {user_obj.email} successfully {status_str}.")
    return redirect('analytics:admin_users')


@login_required
@admin_required
def admin_manage_companies(request):
    """
    Admin company management with verification approval/rejection.
    """
    status_filter = request.GET.get('status')
    search = request.GET.get('search')

    companies = Company.objects.all().order_by('-created_at')

    if status_filter:
        companies = companies.filter(verification_status=status_filter)

    if search:
        companies = companies.filter(
            Q(name__icontains=search) |
            Q(location__icontains=search) |
            Q(industry__icontains=search)
        )

    context = {
        'companies': companies,
        'selected_status': status_filter,
        'search': search,
        'verification_choices': Company.VerificationStatus.choices,
    }
    return render(request, 'admin_dashboard/manage_companies.html', context)


@login_required
@admin_required
def admin_verify_company(request, pk):
    """
    Verify a company.
    """
    company = get_object_or_404(Company, pk=pk)
    company.verification_status = Company.VerificationStatus.VERIFIED
    company.verified_at = timezone.now()
    company.save()

    # Notify recruiters belonging to company
    for recruiter in company.recruiters.all():
        create_notification(
            user=recruiter.user,
            title="Company Verified!",
            message=f"Congratulations! Your company '{company.name}' has been verified by the administrator. You can now post live opportunities.",
            notification_type=Notification.NotificationType.SYSTEM,
            link_url="/recruiters/dashboard/"
        )

    messages.success(request, f"Company '{company.name}' has been marked as Verified.")
    return redirect('analytics:admin_companies')


@login_required
@admin_required
def admin_reject_company(request, pk):
    """
    Reject a company verification.
    """
    company = get_object_or_404(Company, pk=pk)
    company.verification_status = Company.VerificationStatus.REJECTED
    company.save()

    for recruiter in company.recruiters.all():
        create_notification(
            user=recruiter.user,
            title="Company Verification Rejected",
            message=f"Verification for company '{company.name}' was not approved. Please review your company information.",
            notification_type=Notification.NotificationType.SYSTEM,
            link_url="/recruiters/company/edit/"
        )

    messages.warning(request, f"Company '{company.name}' has been marked as Rejected.")
    return redirect('analytics:admin_companies')


@login_required
@admin_required
def admin_manage_opportunities(request):
    """
    Admin opportunity management and approval queue.
    """
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    search = request.GET.get('search')

    opps = Opportunity.objects.select_related('company', 'recruiter').order_by('-created_at')

    if status_filter:
        opps = opps.filter(status=status_filter)
    if type_filter:
        opps = opps.filter(opportunity_type=type_filter)
    if search:
        opps = opps.filter(
            Q(title__icontains=search) |
            Q(company__name__icontains=search) |
            Q(job_role__icontains=search)
        )

    context = {
        'opportunities': opps,
        'selected_status': status_filter,
        'selected_type': type_filter,
        'search': search,
        'status_choices': Opportunity.Status.choices,
        'type_choices': Opportunity.OpportunityType.choices,
    }
    return render(request, 'admin_dashboard/manage_opportunities.html', context)


@login_required
@admin_required
def admin_approve_opportunity(request, pk):
    """
    Approve an opportunity posting.
    """
    opp = get_object_or_404(Opportunity, pk=pk)
    opp.status = Opportunity.Status.APPROVED
    opp.save(update_fields=['status'])

    # Notify recruiter
    create_notification(
        user=opp.recruiter,
        title=f"Opportunity Approved: {opp.title}",
        message=f"Your posting '{opp.title}' has been approved and is now live for students to apply!",
        notification_type=Notification.NotificationType.OPPORTUNITY,
        link_url=f"/opportunities/{opp.id}/"
    )

    messages.success(request, f"Opportunity '{opp.title}' approved successfully.")
    return redirect('analytics:admin_opportunities')


@login_required
@admin_required
def admin_reject_opportunity(request, pk):
    """
    Reject an opportunity posting.
    """
    opp = get_object_or_404(Opportunity, pk=pk)
    opp.status = Opportunity.Status.REJECTED
    opp.save(update_fields=['status'])

    # Notify recruiter
    create_notification(
        user=opp.recruiter,
        title=f"Opportunity Rejected: {opp.title}",
        message=f"Your posting '{opp.title}' was reviewed and rejected by the administration.",
        notification_type=Notification.NotificationType.OPPORTUNITY,
        link_url="/opportunities/my/"
    )

    messages.warning(request, f"Opportunity '{opp.title}' rejected.")
    return redirect('analytics:admin_opportunities')


@login_required
@admin_required
def admin_manage_applications(request):
    """
    View all platform applications.
    """
    status_filter = request.GET.get('status')
    search = request.GET.get('search')

    applications = Application.objects.select_related(
        'student', 'opportunity__company', 'opportunity__recruiter'
    ).order_by('-applied_at')

    if status_filter:
        applications = applications.filter(status=status_filter)
    if search:
        applications = applications.filter(
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search) |
            Q(student__email__icontains=search) |
            Q(opportunity__title__icontains=search) |
            Q(opportunity__company__name__icontains=search)
        )

    context = {
        'applications': applications,
        'selected_status': status_filter,
        'search': search,
        'status_choices': Application.Status.choices,
    }
    return render(request, 'admin_dashboard/manage_applications.html', context)


@login_required
@admin_required
def admin_analytics(request):
    """
    Detailed analytics page with charts and breakdown tables.
    """
    stats = get_platform_overview_stats()
    monthly_apps = get_monthly_applications_data()
    funnel_data = get_application_funnel_data()
    popular_skills = get_popular_skills_data(10)
    top_companies = get_active_companies_data(8)

    context = {
        'stats': stats,
        'monthly_apps': monthly_apps,
        'funnel_data': funnel_data,
        'popular_skills': popular_skills,
        'top_companies': top_companies,
    }
    return render(request, 'admin_dashboard/analytics.html', context)
