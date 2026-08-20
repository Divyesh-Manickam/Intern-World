from functools import wraps
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not (request.user.is_student or request.user.is_admin_user):
            messages.error(request, "Access restricted. This page is only accessible by students.")
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def recruiter_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not (request.user.is_recruiter or request.user.is_admin_user):
            messages.error(request, "Access restricted. This page is only accessible by recruiters.")
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('accounts:login')
        if not request.user.is_admin_user:
            messages.error(request, "Access restricted. Administrator privileges are required.")
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def unauthenticated_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class StudentRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_student or request.user.is_admin_user):
            messages.error(request, "Access restricted to students.")
            return redirect('accounts:dashboard_redirect')
        return super().dispatch(request, *args, **kwargs)


class RecruiterRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_recruiter or request.user.is_admin_user):
            messages.error(request, "Access restricted to recruiters.")
            return redirect('accounts:dashboard_redirect')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin_user:
            messages.error(request, "Access restricted to administrators.")
            return redirect('accounts:dashboard_redirect')
        return super().dispatch(request, *args, **kwargs)
