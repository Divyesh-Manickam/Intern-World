from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from accounts.decorators import recruiter_required
from .models import Interview
from .forms import ScheduleInterviewForm
from applications.models import Application
from notifications.services import create_notification
from notifications.models import Notification


@login_required
def interview_list(request):
    """
    List of interviews for the authenticated user.
    If student -> shows interviews where student=request.user.
    If recruiter -> shows interviews where recruiter=request.user.
    """
    if request.user.is_student:
        interviews = Interview.objects.filter(
            student=request.user
        ).select_related('application__opportunity__company', 'recruiter').order_by('interview_date', 'interview_time')
    elif request.user.is_recruiter:
        interviews = Interview.objects.filter(
            recruiter=request.user
        ).select_related('application__opportunity__company', 'student__student_profile').order_by('interview_date', 'interview_time')
    else:
        interviews = Interview.objects.all().select_related('application__opportunity__company', 'student', 'recruiter').order_by('interview_date', 'interview_time')

    upcoming = [i for i in interviews if i.interview_date >= timezone.now().date() and i.status == Interview.Status.SCHEDULED]
    past = [i for i in interviews if i.interview_date < timezone.now().date() or i.status != Interview.Status.SCHEDULED]

    return render(request, 'interviews/interview_list.html', {
        'upcoming_interviews': upcoming,
        'past_interviews': past,
    })


@login_required
@recruiter_required
def schedule_interview(request, application_id):
    """
    Recruiter schedules an interview for a specific application.
    """
    application = get_object_or_404(
        Application,
        pk=application_id,
        opportunity__recruiter=request.user
    )

    if request.method == 'POST':
        form = ScheduleInterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.recruiter = request.user
            interview.student = application.student
            interview.status = Interview.Status.SCHEDULED
            interview.save()

            # Update application status
            application.status = Application.Status.INTERVIEW_SCHEDULED
            application.save(update_fields=['status'])

            # Send notification to student
            create_notification(
                user=application.student,
                title=f"Interview Scheduled: {application.opportunity.title}",
                message=(
                    f"Great news! An interview has been scheduled for '{application.opportunity.title}' "
                    f"at {application.opportunity.company.name} on {interview.interview_date} at {interview.interview_time}. "
                    f"Format: {interview.get_interview_type_display()}."
                ),
                notification_type=Notification.NotificationType.INTERVIEW,
                link_url="/interviews/"
            )

            messages.success(
                request,
                f"Interview successfully scheduled with {application.student.get_full_name()} for {interview.interview_date}."
            )
            return redirect('recruiters:applicant_detail', pk=application.id)
        else:
            for err in form.errors.values():
                messages.error(request, err)
    else:
        form = ScheduleInterviewForm()

    return render(request, 'interviews/schedule_modal.html', {
        'form': form,
        'application': application
    })


@login_required
def cancel_interview(request, pk):
    """
    Cancel an existing interview.
    """
    if request.user.is_recruiter:
        interview = get_object_or_404(Interview, pk=pk, recruiter=request.user)
    elif request.user.is_admin_user:
        interview = get_object_or_404(Interview, pk=pk)
    else:
        messages.error(request, "Permission denied.")
        return redirect('interviews:interview_list')

    interview.status = Interview.Status.CANCELLED
    interview.save(update_fields=['status'])

    # Notify student
    create_notification(
        user=interview.student,
        title=f"Interview Cancelled: {interview.application.opportunity.title}",
        message=f"The interview scheduled for '{interview.application.opportunity.title}' on {interview.interview_date} has been cancelled by the recruiter.",
        notification_type=Notification.NotificationType.INTERVIEW,
        link_url="/interviews/"
    )

    messages.info(request, "Interview cancelled successfully.")
    return redirect('interviews:interview_list')
