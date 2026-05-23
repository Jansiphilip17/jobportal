from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Job, JobCategory, JobSkill, JobSkillMapping
from .forms import JobForm
from companies.models import Company
from applications.models import Application
from candidates.models import SavedJob


# ── Home ──────────────────────────────────────────────────────────────────────
def home(request):
    featured_jobs = Job.objects.filter(
        is_active=True, is_approved=True
    ).select_related('company').order_by('-is_featured', '-created_at')[:6]

    from companies.models import Company as Co
    top_companies = Co.objects.filter(is_active=True, is_verified=True)[:8]

    from accounts.models import User
    stats = {
        'jobs':       Job.objects.filter(is_active=True, is_approved=True).count(),
        'companies':  Co.objects.filter(is_active=True).count(),
        'candidates': User.objects.filter(role=User.CANDIDATE).count(),
    }
    return render(request, 'home.html', {
        'featured_jobs': featured_jobs,
        'top_companies': top_companies,
        'stats': stats,
    })


# ── Job List ──────────────────────────────────────────────────────────────────
def job_list(request):
    jobs = Job.objects.filter(
        is_active=True, is_approved=True
    ).select_related('company', 'category')

    q          = request.GET.get('q', '')
    location   = request.GET.get('location', '')
    job_types  = request.GET.getlist('job_type')
    experience = request.GET.get('experience', '')
    min_salary = request.GET.get('min_salary', '')
    category   = request.GET.get('category', '')
    sort       = request.GET.get('sort', '-created_at')

    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(company__name__icontains=q)
        ).distinct()
    if location:
        jobs = jobs.filter(
            Q(location__icontains=location) | Q(is_remote=True)
        )
    if job_types:
        jobs = jobs.filter(job_type__in=job_types)
    if experience:
        jobs = jobs.filter(experience_required=experience)
    if min_salary:
        jobs = jobs.filter(min_salary__gte=min_salary)
    if category:
        jobs = jobs.filter(category__slug=category)

    jobs = jobs.order_by(sort)

    saved_job_ids = []
    if request.user.is_authenticated and request.user.is_candidate:
        try:
            profile = request.user.candidate_profile
            saved_job_ids = list(
                SavedJob.objects.filter(candidate=profile).values_list('job_id', flat=True)
            )
        except Exception:
            pass

    paginator  = Paginator(jobs, 10)
    page       = request.GET.get('page', 1)
    jobs_page  = paginator.get_page(page)

    # rebuild filter params without page
    filter_params = request.GET.urlencode()
    filter_params = '&'.join(
        p for p in filter_params.split('&') if not p.startswith('page')
    )

    return render(request, 'jobs/list.html', {
        'jobs':               jobs_page,
        'total_jobs':         paginator.count,
        'is_paginated':       paginator.num_pages > 1,
        'page_obj':           jobs_page,
        'categories':         JobCategory.objects.all(),
        'job_types':          Job.JOB_TYPE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
        'selected_job_types': job_types,
        'saved_job_ids':      saved_job_ids,
        'filter_params':      filter_params,
    })


# ── Job Detail ────────────────────────────────────────────────────────────────
def job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug, is_active=True)
    job.views_count += 1
    job.save(update_fields=['views_count'])

    already_applied = False
    is_saved        = False

    if request.user.is_authenticated and request.user.is_candidate:
        already_applied = Application.objects.filter(
            candidate=request.user, job=job
        ).exists()
        try:
            profile  = request.user.candidate_profile
            is_saved = SavedJob.objects.filter(candidate=profile, job=job).exists()
        except Exception:
            pass

    return render(request, 'jobs/detail.html', {
        'job':             job,
        'already_applied': already_applied,
        'is_saved':        is_saved,
    })


# ── Post Job ──────────────────────────────────────────────────────────────────
@login_required
def post_job(request):
    if not request.user.is_recruiter:
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('jobs:list')

    # Recruiter must have a company first
    companies = Company.objects.filter(recruiter=request.user)
    if not companies.exists():
        messages.warning(request, 'Please create a company profile first.')
        return redirect('companies:create')

    if request.method == 'POST':
        form = JobForm(request.POST, recruiter=request.user)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user

            # Auto-generate unique slug from title
            base_slug = slugify(job.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            job.slug = slug
            job.save()

            # Save skills from hidden input (comma-separated)
            skills_str = request.POST.get('skills', '')
            for skill_name in [s.strip() for s in skills_str.split(',') if s.strip()]:
                skill_slug = slugify(skill_name)
                skill, _ = JobSkill.objects.get_or_create(
                    slug=skill_slug,
                    defaults={'name': skill_name}
                )
                JobSkillMapping.objects.get_or_create(job=job, skill=skill)

            messages.success(request, f'Job "{job.title}" posted! It will go live after admin approval.')
            return redirect('recruiters:my_jobs')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = JobForm(recruiter=request.user)

    return render(request, 'jobs/post_job.html', {
        'form':       form,
        'companies':  companies,
        'categories': JobCategory.objects.all(),
    })


# ── Edit Job ──────────────────────────────────────────────────────────────────
@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job, recruiter=request.user)
        if form.is_valid():
            form.save()
            # Update skills
            JobSkillMapping.objects.filter(job=job).delete()
            skills_str = request.POST.get('skills', '')
            for skill_name in [s.strip() for s in skills_str.split(',') if s.strip()]:
                skill_slug = slugify(skill_name)
                skill, _ = JobSkill.objects.get_or_create(
                    slug=skill_slug,
                    defaults={'name': skill_name}
                )
                JobSkillMapping.objects.get_or_create(job=job, skill=skill)

            messages.success(request, 'Job updated successfully.')
            return redirect('recruiters:my_jobs')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = JobForm(instance=job, recruiter=request.user)

    return render(request, 'jobs/post_job.html', {
        'form':            form,
        'job':             job,
        'companies':       Company.objects.filter(recruiter=request.user),
        'categories':      JobCategory.objects.all(),
        'existing_skills': job.skills_required.all(),
    })


# ── Delete Job ────────────────────────────────────────────────────────────────
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    title = job.title
    job.delete()
    messages.success(request, f'Job "{title}" deleted.')
    return redirect('recruiters:my_jobs')