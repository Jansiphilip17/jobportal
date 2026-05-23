from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from jobs.models import Job
from applications.models import Application, ApplicationStatusHistory
from notifications.models import Notification


def recruiter_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_recruiter:
            messages.error(request, 'Recruiter access required.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@recruiter_required
def my_jobs(request):
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    return render(request, 'recruiters/my_jobs.html', {'jobs': jobs})


@login_required
@recruiter_required
def job_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = Application.objects.filter(job=job).select_related(
        'candidate', 'candidate__candidate_profile', 'resume'
    ).prefetch_related('candidate__candidate_profile__skills').order_by('-applied_at')

    pipeline_counts = {
        'Applied': applications.filter(status='applied').count(),
        'Shortlisted': applications.filter(status='shortlisted').count(),
        'Interview': applications.filter(status='interview_scheduled').count(),
        'Selected': applications.filter(status='selected').count(),
        'Rejected': applications.filter(status='rejected').count(),
    }

    return render(request, 'recruiters/job_applicants.html', {
        'job': job,
        'applications': applications,
        'status_choices': Application.STATUS_CHOICES,
        'pipeline_counts': pipeline_counts,
    })


@login_required
@recruiter_required
def all_applicants(request):
    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related('candidate', 'job').order_by('-applied_at')
    return render(request, 'recruiters/all_applicants.html', {
        'applications': applications,
        'status_choices': Application.STATUS_CHOICES,
    })


@login_required
@recruiter_required
def application_detail(request, app_id):
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    if not application.is_seen_by_recruiter:
        application.is_seen_by_recruiter = True
        application.save(update_fields=['is_seen_by_recruiter'])
    return render(request, 'recruiters/application_detail.html', {
        'application': application,
        'status_choices': Application.STATUS_CHOICES,
    })


@login_required
@recruiter_required
def update_application_status(request, app_id):
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            old_status = application.status
            application.status = new_status
            application.save()
            ApplicationStatusHistory.objects.create(
                application=application,
                status=new_status,
                changed_by=request.user,
            )
            # Notify candidate
            status_messages = {
                'shortlisted': f'Congratulations! You were shortlisted for {application.job.title}',
                'interview_scheduled': f'Interview scheduled for {application.job.title}',
                'selected': f'🎉 You were selected for {application.job.title}!',
                'rejected': f'Update on your application for {application.job.title}',
            }
            if new_status in status_messages:
                Notification.objects.create(
                    recipient=application.candidate,
                    title=status_messages[new_status],
                    message=status_messages[new_status],
                    notification_type=new_status if new_status in ['shortlist', 'interview'] else 'application',
                    link=f'/applications/my-applications/',
                )
            messages.success(request, f'Status updated to {application.get_status_display()}')

    return redirect(request.META.get('HTTP_REFERER', 'recruiters:all_applicants'))
