from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import secrets
import hashlib
from datetime import timedelta

from .models import User, EmailVerificationToken, PasswordResetToken
from .forms import (CandidateRegistrationForm, RecruiterRegistrationForm, LoginForm,
                    UserUpdateForm, PasswordChangeForm, ForgotPasswordForm, ResetPasswordForm)


def home(request):
    from jobs.models import Job
    from companies.models import Company
    featured_jobs = Job.objects.filter(is_active=True, is_approved=True).order_by('-created_at')[:6]
    top_companies = Company.objects.filter(is_verified=True).order_by('-created_at')[:8]
    stats = {
        'jobs': Job.objects.filter(is_active=True).count(),
        'companies': Company.objects.filter(is_verified=True).count(),
        'candidates': User.objects.filter(role=User.CANDIDATE).count(),
    }
    return render(request, 'home.html', {
        'featured_jobs': featured_jobs,
        'top_companies': top_companies,
        'stats': stats
    })


def register_candidate(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            _send_verification_email(request, user)
            messages.success(request, 'Account created! Please verify your email to continue.')
            return redirect('accounts:login')
    else:
        form = CandidateRegistrationForm()
    return render(request, 'accounts/register_candidate.html', {'form': form})


def register_recruiter(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = RecruiterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            _send_verification_email(request, user)
            messages.success(request, 'Recruiter account created! Please verify your email.')
            return redirect('accounts:login')
    else:
        form = RecruiterRegistrationForm()
    return render(request, 'accounts/register_recruiter.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


def verify_email(request, token):
    try:
        verification = EmailVerificationToken.objects.get(token=token, is_used=False)
        if verification.expires_at < timezone.now():
            messages.error(request, 'Verification link has expired. Please request a new one.')
            return redirect('accounts:login')
        verification.user.is_verified = True
        verification.user.save()
        verification.is_used = True
        verification.save()
        messages.success(request, 'Email verified successfully! You can now login.')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    return redirect('accounts:login')


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                _send_password_reset_email(request, user)
                messages.success(request, 'Password reset link sent to your email.')
            except User.DoesNotExist:
                messages.success(request, 'If that email exists, a reset link was sent.')
            return redirect('accounts:login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        if reset_token.expires_at < timezone.now():
            messages.error(request, 'Reset link has expired.')
            return redirect('accounts:forgot_password')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid reset link.')
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            reset_token.user.set_password(form.cleaned_data['new_password'])
            reset_token.user.save()
            reset_token.is_used = True
            reset_token.save()
            messages.success(request, 'Password reset successfully!')
            return redirect('accounts:login')
    else:
        form = ResetPasswordForm()
    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})


@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile_settings')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_settings.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['old_password']):
                messages.error(request, 'Current password is incorrect.')
            else:
                request.user.set_password(form.cleaned_data['new_password'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully!')
                return redirect('accounts:profile_settings')
    else:
        form = PasswordChangeForm()
    return render(request, 'accounts/change_password.html', {'form': form})


def _send_verification_email(request, user):
    token = secrets.token_urlsafe(32)
    EmailVerificationToken.objects.filter(user=user).delete()
    EmailVerificationToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(hours=24)
    )
    verify_url = request.build_absolute_uri(f'/accounts/verify-email/{token}/')
    send_mail(
        subject='Verify your JobPortal account',
        message=f'Click the link to verify: {verify_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def _send_password_reset_email(request, user):
    token = secrets.token_urlsafe(32)
    PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(hours=2)
    )
    reset_url = request.build_absolute_uri(f'/accounts/reset-password/{token}/')
    send_mail(
        subject='Reset your JobPortal password',
        message=f'Click the link to reset your password: {reset_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
