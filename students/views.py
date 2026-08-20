from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.utils import timezone

from accounts.decorators import student_required
from accounts.forms import UserUpdateForm
from .models import StudentProfile, Project, Certification, Experience
from .forms import StudentProfileForm, ResumeUploadForm, ProjectForm, CertificationForm, ExperienceForm
from .services import extract_text_from_pdf
from opportunities.models import Opportunity, SavedOpportunity
from applications.models import Application
from interviews.models import Interview
from recommendations.services import get_recommendations_for_student


@login_required
@student_required
def student_dashboard(request):
    """
    Main dashboard for students.
    Displays:
    - Profile completion %
    - Summary metrics for applications
    - Recommended internships & placements
    - Upcoming interviews
    - Saved opportunities
    """
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    
    # Application metrics
    apps = Application.objects.filter(student=request.user)
    total_apps = apps.count()
    under_review = apps.filter(status=Application.Status.UNDER_REVIEW).count()
    shortlisted = apps.filter(status=Application.Status.SHORTLISTED).count()
    interviews_count = apps.filter(status=Application.Status.INTERVIEW_SCHEDULED).count()
    selected = apps.filter(status=Application.Status.SELECTED).count()
    rejected = apps.filter(status=Application.Status.REJECTED).count()

    # Upcoming interviews
    upcoming_interviews = Interview.objects.filter(
        student=request.user,
        status=Interview.Status.SCHEDULED,
        interview_date__gte=timezone.now().date()
    ).select_related('application__opportunity__company', 'recruiter').order_by('interview_date', 'interview_time')[:5]

    # Recommendations
    recommended_list = get_recommendations_for_student(request.user, limit=8, min_score=10)
    
    # Separate into internships and placements
    rec_internships = [item for item in recommended_list if item[0].opportunity_type == Opportunity.OpportunityType.INTERNSHIP][:4]
    rec_placements = [item for item in recommended_list if item[0].opportunity_type == Opportunity.OpportunityType.PLACEMENT][:4]

    # Saved opportunities
    saved_ids = list(SavedOpportunity.objects.filter(student=request.user).values_list('opportunity_id', flat=True))
    saved_opps = Opportunity.objects.filter(id__in=saved_ids)[:4]

    context = {
        'profile': profile,
        'completion_percentage': profile.completion_percentage,
        'total_apps': total_apps,
        'under_review': under_review,
        'shortlisted': shortlisted,
        'interviews_count': interviews_count,
        'selected': selected,
        'rejected': rejected,
        'upcoming_interviews': upcoming_interviews,
        'rec_internships': rec_internships,
        'rec_placements': rec_placements,
        'saved_opps': saved_opps,
        'saved_ids': saved_ids,
    }
    return render(request, 'students/dashboard.html', context)


@login_required
@student_required
def student_profile(request):
    """
    Public/internal read view of student profile.
    """
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    return render(request, 'students/profile.html', {
        'profile': profile,
        'completion_percentage': profile.completion_percentage,
    })


class StudentProfileEditView(View):
    template_name = 'students/edit_profile.html'

    @method_decorator(login_required)
    @method_decorator(student_required)
    def get(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(instance=request.user)
        profile_form = StudentProfileForm(instance=profile)
        resume_form = ResumeUploadForm(instance=profile)
        project_form = ProjectForm()
        cert_form = CertificationForm()
        exp_form = ExperienceForm()

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'resume_form': resume_form,
            'project_form': project_form,
            'cert_form': cert_form,
            'exp_form': exp_form,
            'profile': profile,
        })

    @method_decorator(login_required)
    @method_decorator(student_required)
    def post(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = StudentProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('students:profile')

        resume_form = ResumeUploadForm(instance=profile)
        project_form = ProjectForm()
        cert_form = CertificationForm()
        exp_form = ExperienceForm()
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'resume_form': resume_form,
            'project_form': project_form,
            'cert_form': cert_form,
            'exp_form': exp_form,
            'profile': profile,
        })


@login_required
@student_required
def upload_resume(request):
    """
    Handles PDF resume uploads and triggers pypdf text extraction.
    """
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            saved_profile = form.save()
            # Extract text from uploaded resume
            if saved_profile.resume:
                extracted_text = extract_text_from_pdf(saved_profile.resume)
                saved_profile.resume_extracted_text = extracted_text
                saved_profile.save(update_fields=['resume_extracted_text'])
            messages.success(request, "Resume uploaded and indexed successfully!")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('students:profile')


@login_required
@student_required
def add_project(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.student = profile
            project.save()
            messages.success(request, f"Project '{project.title}' added.")
        else:
            messages.error(request, "Error adding project. Please check the inputs.")
    return redirect('students:edit_profile')


@login_required
@student_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, student__user=request.user)
    project.delete()
    messages.info(request, "Project removed.")
    return redirect('students:edit_profile')


@login_required
@student_required
def add_certification(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.student = profile
            cert.save()
            messages.success(request, f"Certification '{cert.name}' added.")
        else:
            messages.error(request, "Error adding certification. Please check the inputs.")
    return redirect('students:edit_profile')


@login_required
@student_required
def delete_certification(request, pk):
    cert = get_object_or_404(Certification, pk=pk, student__user=request.user)
    cert.delete()
    messages.info(request, "Certification removed.")
    return redirect('students:edit_profile')


@login_required
@student_required
def add_experience(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.student = profile
            exp.save()
            messages.success(request, f"Experience at '{exp.company}' added.")
        else:
            messages.error(request, "Error adding experience. Please check the inputs.")
    return redirect('students:edit_profile')


@login_required
@student_required
def delete_experience(request, pk):
    exp = get_object_or_404(Experience, pk=pk, student__user=request.user)
    exp.delete()
    messages.info(request, "Experience removed.")
    return redirect('students:edit_profile')


@login_required
@student_required
def saved_opportunities(request):
    """
    Displays list of opportunities saved by student.
    """
    saved_items = SavedOpportunity.objects.filter(
        student=request.user
    ).select_related('opportunity__company', 'opportunity__recruiter')
    return render(request, 'students/saved_opportunities.html', {'saved_items': saved_items})


@login_required
@student_required
def toggle_save_opportunity(request, pk):
    """
    Toggle saving/unsaving an opportunity. Supports both AJAX and regular POST.
    """
    opportunity = get_object_or_404(Opportunity, pk=pk)
    saved_obj = SavedOpportunity.objects.filter(student=request.user, opportunity=opportunity).first()
    
    if saved_obj:
        saved_obj.delete()
        is_saved = False
        msg = f"Removed '{opportunity.title}' from your saved list."
    else:
        SavedOpportunity.objects.create(student=request.user, opportunity=opportunity)
        is_saved = True
        msg = f"Saved '{opportunity.title}' for later."

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_saved': is_saved, 'message': msg})

    messages.info(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'students:dashboard'))
