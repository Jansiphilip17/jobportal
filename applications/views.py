from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Application, ApplicationStatusHistory
from jobs.models import Job
from candidates.models import Resume, CandidateProfile, SavedJob
from notifications.models import Notification


@login_required
def apply_job(request, slug):
    if not request.user.is_candidate:
        messages.error(request, 'Only candidates can apply for jobs.')
        return redirect('jobs:detail', slug=slug)

    job = get_object_or_404(Job, slug=slug, is_active=True, is_approved=True)

    if Application.objects.filter(candidate=request.user, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('applications:my_applications')

    try:
        profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        messages.error(request, 'Please complete your candidate profile first.')
        return redirect('candidates:profile')

    resumes = Resume.objects.filter(candidate=profile)

    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        cover_letter = request.POST.get('cover_letter', '')
        resume = Resume.objects.filter(id=resume_id, candidate=profile).first()

        application = Application.objects.create(
            candidate=request.user,
            job=job,
            resume=resume,
            cover_letter=cover_letter,
            status='applied',
        )
        ApplicationStatusHistory.objects.create(
            application=application,
            status='applied',
            changed_by=request.user,
            notes='Application submitted',
        )
        job.applications_count += 1
        job.save(update_fields=['applications_count'])

        # Notify recruiter
        Notification.objects.create(
            recipient=job.recruiter,
            title=f'New application for {job.title}',
            message=f'{request.user.get_full_name()} applied for {job.title}',
            notification_type='application',
            link=f'/recruiters/applications/{application.id}/',
        )

        messages.success(request, f'Application submitted for {job.title}!')
        return redirect('applications:my_applications')

    return render(request, 'applications/apply.html', {'job': job, 'resumes': resumes})


@login_required
def my_applications(request):
    if not request.user.is_candidate:
        return redirect('dashboard:index')

    applications = Application.objects.filter(
        candidate=request.user
    ).select_related('job', 'job__company').prefetch_related('interviews').order_by('-applied_at')

    status_steps = [
        ('applied', 'Applied'),
        ('under_review', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview'),
        ('selected', 'Selected'),
    ]

    return render(request, 'applications/my_applications.html', {
        'applications': applications,
        'status_steps': status_steps,
    })


@login_required
def withdraw_application(request, app_id):
    app = get_object_or_404(Application, id=app_id, candidate=request.user)
    if app.status in ['applied', 'under_review']:
        app.status = 'withdrawn'
        app.save()
        messages.success(request, 'Application withdrawn.')
    else:
        messages.error(request, 'Cannot withdraw this application.')
    return redirect('applications:my_applications')


@login_required
def save_job(request, job_id):
    """Toggle save/unsave a job. Returns JSON."""
    if not request.user.is_candidate:
        return JsonResponse({'error': 'Not a candidate'}, status=403)

    job = get_object_or_404(Job, id=job_id)
    try:
        profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        return JsonResponse({'error': 'No profile'}, status=400)

    saved, created = SavedJob.objects.get_or_create(candidate=profile, job=job)
    if not created:
        saved.delete()
        return JsonResponse({'saved': False})
    return JsonResponse({'saved': True})
