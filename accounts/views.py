from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator

from .forms import StudentRegistrationForm, RecruiterRegistrationForm, UserLoginForm, UserUpdateForm
from .decorators import unauthenticated_user
from .models import User


class LoginView(View):
    template_name = 'accounts/login.html'

    @method_decorator(unauthenticated_user)
    def get(self, request):
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})

    @method_decorator(unauthenticated_user)
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
        
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out successfully.")
        return redirect('accounts:login')

    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out successfully.")
        return redirect('accounts:login')


class StudentRegisterView(View):
    template_name = 'accounts/register_student.html'

    @method_decorator(unauthenticated_user)
    def get(self, request):
        form = StudentRegistrationForm()
        return render(request, self.template_name, {'form': form})

    @method_decorator(unauthenticated_user)
    def post(self, request):
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to InternWorld! Your student profile has been created.")
            return redirect('students:dashboard')
        return render(request, self.template_name, {'form': form})


class RecruiterRegisterView(View):
    template_name = 'accounts/register_recruiter.html'

    @method_decorator(unauthenticated_user)
    def get(self, request):
        form = RecruiterRegistrationForm()
        return render(request, self.template_name, {'form': form})

    @method_decorator(unauthenticated_user)
    def post(self, request):
        form = RecruiterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Welcome to InternWorld! Your recruiter account has been created. "
                "Your company is currently under review by our administration team."
            )
            return redirect('recruiters:dashboard')
        return render(request, self.template_name, {'form': form})


@login_required
def dashboard_redirect(request):
    """
    Directs authenticated user to their role-specific dashboard.
    """
    user = request.user
    if user.is_admin_user:
        return redirect('analytics:admin_dashboard')
    elif user.is_recruiter:
        return redirect('recruiters:dashboard')
    elif user.is_student:
        return redirect('students:dashboard')
    return redirect('opportunities:list')
