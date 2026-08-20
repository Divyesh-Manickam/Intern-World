from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.utils import timezone

from accounts.decorators import student_required
from .models import Application
from .forms import ApplicationSubmitForm
from opportunities.models import Opportunity
from notifications.services import create_notification
from notifications.models import Notification


@login_required
@student_required
def apply_opportunity(request, pk):
    """
    Handle student application submission to an opportunity.
    """
    opportunity = get_object_or_404(Opportunity, pk=pk)

    # 1. Check if opportunity is active
    if not opportunity.is_active:
        messages.error(request, "This opportunity is closed or the application deadline has passed.")
        return redirect('opportunities:detail', pk=pk)

    # 2. Check for duplicate application
    if Application.objects.filter(student=request.user, opportunity=opportunity).exists():
        messages.warning(request, "You have already submitted an application for this opportunity.")
        return redirect('opportunities:detail', pk=pk)

    profile = getattr(request.user, 'student_profile', None)

    if request.method == 'POST':
        form = ApplicationSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_resume = form.cleaned_data.get('resume')
            # Check if student has a resume attached or uploaded
            final_resume = uploaded_resume or (profile.resume if profile else None)

            if not final_resume:
                messages.error(request, "Please upload your resume before submitting your application.")
                return redirect('students:edit_profile')

            try:
                application = form.save(commit=False)
                application.student = request.user
                application.opportunity = opportunity
                application.resume = final_resume
                application.status = Application.Status.APPLIED
                application.save()

                # Send notification to recruiter
                create_notification(
                    user=opportunity.recruiter,
                    title=f"New Applicant: {opportunity.title}",
                    message=f"{request.user.get_full_name()} has applied for '{opportunity.title}'.",
                    notification_type=Notification.NotificationType.APPLICATION,
                    link_url=f"/recruiters/applicants/{application.id}/"
                )

                # Send confirmation notification to student
                create_notification(
                    user=request.user,
                    title=f"Application Received: {opportunity.title}",
                    message=f"Your application for '{opportunity.title}' at {opportunity.company.name} was successfully submitted!",
                    notification_type=Notification.NotificationType.APPLICATION,
                    link_url="/applications/my-applications/"
                )

                messages.success(request, f"Successfully applied for '{opportunity.title}' at {opportunity.company.name}!")
                return redirect('applications:my_applications')

            except IntegrityError:
                messages.warning(request, "You have already applied for this opportunity.")
                return redirect('opportunities:detail', pk=pk)
        else:
            for err in form.errors.values():
                messages.error(request, err)

    return redirect('opportunities:detail', pk=pk)


@login_required
@student_required
def my_applications(request):
    """
    List of applications submitted by current student with status filtering.
    """
    applications = Application.objects.filter(
        student=request.user
    ).select_related(
        'opportunity__company', 'opportunity__recruiter'
    ).prefetch_related('interviews').order_by('-applied_at')

    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'applications': applications,
        'selected_status': status_filter,
        'status_choices': Application.Status.choices,
    }
    return render(request, 'applications/my_applications.html', context)


@login_required
@student_required
def application_detail(request, pk):
    """
    Student view of an application's details and interview schedule.
    """
    application = get_object_or_404(
        Application.objects.select_related('opportunity__company', 'opportunity__recruiter'),
        pk=pk,
        student=request.user
    )
    interviews = application.interviews.all().order_by('-interview_date')

    return render(request, 'applications/application_detail.html', {
        'application': application,
        'interviews': interviews,
    })


@login_required
@student_required
def withdraw_application(request, pk):
    """
    Allows student to withdraw an active application.
    """
    application = get_object_or_404(Application, pk=pk, student=request.user)

    if application.status in [Application.Status.SELECTED, Application.Status.REJECTED, Application.Status.WITHDRAWN]:
        messages.warning(request, f"Cannot withdraw an application that is already '{application.get_status_display()}'.")
        return redirect('applications:my_applications')

    application.status = Application.Status.WITHDRAWN
    application.save(update_fields=['status'])

    # Notify recruiter
    create_notification(
        user=application.opportunity.recruiter,
        title=f"Application Withdrawn: {application.opportunity.title}",
        message=f"{request.user.get_full_name()} has withdrawn their application for '{application.opportunity.title}'.",
        notification_type=Notification.NotificationType.APPLICATION,
        link_url=f"/recruiters/applicants/{application.id}/"
    )

    messages.info(request, f"Your application for '{application.opportunity.title}' has been withdrawn.")
    return redirect('applications:my_applications')
