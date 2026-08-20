from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.db.models import Q

from accounts.decorators import recruiter_required
from accounts.forms import UserUpdateForm
from .models import Company, RecruiterProfile
from .forms import CompanyForm, RecruiterProfileForm, ApplicantStatusUpdateForm
from opportunities.models import Opportunity
from applications.models import Application
from interviews.models import Interview
from notifications.services import create_notification
from notifications.models import Notification
from analytics.services import get_recruiter_dashboard_stats, get_application_funnel_data


@login_required
@recruiter_required
def recruiter_dashboard(request):
    """
    Main recruiter dashboard displaying key hiring metrics, recent applications, and job postings.
    """
    profile, _ = RecruiterProfile.objects.get_or_create(user=request.user)
    company = profile.company
    stats = get_recruiter_dashboard_stats(request.user)

    recent_applications = Application.objects.filter(
        opportunity__recruiter=request.user
    ).select_related('student__student_profile', 'opportunity').order_by('-applied_at')[:8]

    my_opportunities = Opportunity.objects.filter(
        recruiter=request.user
    ).order_by('-created_at')[:5]

    funnel_data = get_application_funnel_data(request.user)

    context = {
        'profile': profile,
        'company': company,
        'stats': stats,
        'recent_applications': recent_applications,
        'my_opportunities': my_opportunities,
        'funnel_data': funnel_data,
    }
    return render(request, 'recruiters/dashboard.html', context)


@login_required
@recruiter_required
def company_profile(request):
    """
    View company profile details.
    """
    profile, _ = RecruiterProfile.objects.get_or_create(user=request.user)
    company = profile.company
    return render(request, 'recruiters/company_profile.html', {
        'profile': profile,
        'company': company,
    })


class CompanyEditView(View):
    template_name = 'recruiters/edit_company.html'

    @method_decorator(login_required)
    @method_decorator(recruiter_required)
    def get(self, request):
        profile, _ = RecruiterProfile.objects.get_or_create(user=request.user)
        company = profile.company
        user_form = UserUpdateForm(instance=request.user)
        recruiter_form = RecruiterProfileForm(instance=profile)
        company_form = CompanyForm(instance=company) if company else CompanyForm()

        return render(request, self.template_name, {
            'user_form': user_form,
            'recruiter_form': recruiter_form,
            'company_form': company_form,
            'company': company,
        })

    @method_decorator(login_required)
    @method_decorator(recruiter_required)
    def post(self, request):
        profile, _ = RecruiterProfile.objects.get_or_create(user=request.user)
        company = profile.company
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        recruiter_form = RecruiterProfileForm(request.POST, instance=profile)
        company_form = CompanyForm(request.POST, request.FILES, instance=company) if company else CompanyForm(request.POST, request.FILES)

        if user_form.is_valid() and recruiter_form.is_valid() and company_form.is_valid():
            user_form.save()
            recruiter_obj = recruiter_form.save(commit=False)
            saved_company = company_form.save()
            recruiter_obj.company = saved_company
            recruiter_obj.save()
            messages.success(request, "Company & Recruiter Profile updated successfully.")
            return redirect('recruiters:company_profile')

        return render(request, self.template_name, {
            'user_form': user_form,
            'recruiter_form': recruiter_form,
            'company_form': company_form,
            'company': company,
        })


@login_required
@recruiter_required
def applicant_management(request):
    """
    Recruiter applicant management portal.
    Allows searching and multi-criteria filtering across all candidates who applied.
    """
    recruiter = request.user
    applications = Application.objects.filter(
        opportunity__recruiter=recruiter
    ).select_related('student__student_profile', 'opportunity__company').order_by('-applied_at')

    # Filter parameters
    opportunity_id = request.GET.get('opportunity')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    min_cgpa = request.GET.get('min_cgpa')
    department = request.GET.get('department')
    grad_year = request.GET.get('grad_year')

    if opportunity_id:
        applications = applications.filter(opportunity_id=opportunity_id)
    if status_filter:
        applications = applications.filter(status=status_filter)
    if search_query:
        applications = applications.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__email__icontains=search_query) |
            Q(student__student_profile__skills__icontains=search_query) |
            Q(opportunity__title__icontains=search_query)
        )
    if min_cgpa:
        try:
            applications = applications.filter(student__student_profile__cgpa__gte=float(min_cgpa))
        except ValueError:
            pass
    if department:
        applications = applications.filter(student__student_profile__department__icontains=department)
    if grad_year:
        try:
            applications = applications.filter(student__student_profile__graduation_year=int(grad_year))
        except ValueError:
            pass

    # Opportunities list for dropdown filter
    my_opportunities = Opportunity.objects.filter(recruiter=recruiter)

    context = {
        'applications': applications,
        'my_opportunities': my_opportunities,
        'selected_opportunity': opportunity_id,
        'selected_status': status_filter,
        'search_query': search_query,
        'min_cgpa': min_cgpa,
        'selected_department': department,
        'selected_grad_year': grad_year,
        'status_choices': Application.Status.choices,
    }
    return render(request, 'recruiters/applicants.html', context)


@login_required
@recruiter_required
def applicant_detail(request, pk):
    """
    Detailed candidate evaluation view.
    """
    application = get_object_or_404(
        Application.objects.select_related(
            'student__student_profile', 'opportunity__company'
        ),
        pk=pk,
        opportunity__recruiter=request.user
    )

    student = application.student
    profile = getattr(student, 'student_profile', None)
    projects = profile.projects.all() if profile else []
    certifications = profile.certifications.all() if profile else []
    experiences = profile.experiences.all() if profile else []
    scheduled_interviews = application.interviews.all().order_by('-interview_date')

    status_form = ApplicantStatusUpdateForm(instance=application)

    context = {
        'application': application,
        'student': student,
        'profile': profile,
        'projects': projects,
        'certifications': certifications,
        'experiences': experiences,
        'scheduled_interviews': scheduled_interviews,
        'status_form': status_form,
    }
    return render(request, 'recruiters/applicant_detail.html', context)


@login_required
@recruiter_required
def update_applicant_status(request, pk):
    """
    POST handler to update application status, add notes, and trigger notification.
    """
    application = get_object_or_404(
        Application,
        pk=pk,
        opportunity__recruiter=request.user
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('recruiter_notes', '')

        if new_status in Application.Status.values:
            old_status = application.status
            application.status = new_status
            application.recruiter_notes = notes
            application.save()

            # Trigger notification to student if status changed
            if old_status != new_status:
                status_display = application.get_status_display()
                create_notification(
                    user=application.student,
                    title=f"Application Update: {application.opportunity.title}",
                    message=f"Your application status for '{application.opportunity.title}' at {application.opportunity.company.name} has been updated to: {status_display}.",
                    notification_type=Notification.NotificationType.APPLICATION,
                    link_url=f"/applications/my-applications/"
                )

            messages.success(request, f"Candidate status successfully updated to '{application.get_status_display()}'.")
        else:
            messages.error(request, "Invalid status choice.")

    return redirect('recruiters:applicant_detail', pk=pk)
