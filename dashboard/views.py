from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from applications.models import Application
from jobs.models import Job
from candidates.models import SavedJob
from interviews.models import Interview


@login_required
def dashboard_index(request):
    user = request.user

    if user.is_candidate:
        return candidate_dashboard(request)
    elif user.is_recruiter:
        return recruiter_dashboard(request)
    elif user.is_staff:
        return redirect('/admin/')
    return redirect('jobs:list')


def candidate_dashboard(request):
    user = request.user
    profile = getattr(user, 'candidate_profile', None)

    recent_applications = Application.objects.filter(
        candidate=user
    ).select_related('job', 'job__company').order_by('-applied_at')[:5]

    stats = {
        'total_applications': Application.objects.filter(candidate=user).count(),
        'shortlisted': Application.objects.filter(candidate=user, status='shortlisted').count(),
        'interviews': Application.objects.filter(candidate=user, status='interview_scheduled').count(),
        'saved_jobs': SavedJob.objects.filter(candidate=profile).count() if profile else 0,
    }

    recommended_jobs = Job.objects.filter(is_active=True, is_approved=True).order_by('-created_at')[:4]

    if profile:
        profile.profile_completion = profile.calculate_completion()
        profile.save(update_fields=['profile_completion'])

    return render(request, 'dashboard/candidate_dashboard.html', {
        'profile': profile,
        'recent_applications': recent_applications,
        'stats': stats,
        'recommended_jobs': recommended_jobs,
    })


def recruiter_dashboard(request):
    user = request.user

    active_jobs = Job.objects.filter(recruiter=user, is_active=True).order_by('-created_at')[:10]

    recent_applicants = Application.objects.filter(
        job__recruiter=user
    ).select_related('candidate', 'job').order_by('-applied_at')[:5]

    stats = {
        'active_jobs': Job.objects.filter(recruiter=user, is_active=True).count(),
        'total_applicants': Application.objects.filter(job__recruiter=user).count(),
        'shortlisted': Application.objects.filter(job__recruiter=user, status='shortlisted').count(),
        'interviews_scheduled': Application.objects.filter(job__recruiter=user, status='interview_scheduled').count(),
    }

    return render(request, 'dashboard/recruiter_dashboard.html', {
        'active_jobs': active_jobs,
        'recent_applicants': recent_applicants,
        'stats': stats,
    })
