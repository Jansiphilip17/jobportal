from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os

from .models import CandidateProfile, Education, CandidateSkill, WorkExperience, Resume, SavedJob
from django.conf import settings


def candidate_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_candidate:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_or_create_profile(user):
    profile, _ = CandidateProfile.objects.get_or_create(user=user)
    return profile


@login_required
@candidate_required
def profile(request):
    candidate_profile = get_or_create_profile(request.user)
    return render(request, 'candidates/profile.html', {'profile': candidate_profile})


@login_required
@candidate_required
def edit_profile(request):
    candidate_profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        data = request.POST
        candidate_profile.headline = data.get('headline', '')
        candidate_profile.summary = data.get('summary', '')
        candidate_profile.dob = data.get('dob') or None
        candidate_profile.gender = data.get('gender', '')
        candidate_profile.address = data.get('address', '')
        candidate_profile.city = data.get('city', '')
        candidate_profile.state = data.get('state', '')
        candidate_profile.current_company = data.get('current_company', '')
        candidate_profile.current_designation = data.get('current_designation', '')
        candidate_profile.total_experience = data.get('total_experience') or 0
        candidate_profile.current_salary = data.get('current_salary') or None
        candidate_profile.expected_salary = data.get('expected_salary') or None
        candidate_profile.notice_period = data.get('notice_period', '')
        candidate_profile.preferred_locations = data.get('preferred_locations', '')
        candidate_profile.linkedin_url = data.get('linkedin_url', '')
        candidate_profile.github_url = data.get('github_url', '')
        candidate_profile.portfolio_url = data.get('portfolio_url', '')
        candidate_profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('candidates:profile')
    return render(request, 'candidates/edit_profile.html', {'profile': candidate_profile})


@login_required
@candidate_required
def manage_resume(request):
    candidate_profile = get_or_create_profile(request.user)
    resumes = Resume.objects.filter(candidate=candidate_profile)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'upload':
            file = request.FILES.get('resume_file')
            if file:
                if file.size > settings.MAX_UPLOAD_SIZE:
                    messages.error(request, 'File too large. Max 5MB allowed.')
                else:
                    ext = os.path.splitext(file.name)[1].lower().strip('.')
                    if ext not in ['pdf', 'doc', 'docx']:
                        messages.error(request, 'Only PDF, DOC, DOCX allowed.')
                    else:
                        is_default = not resumes.exists()
                        Resume.objects.create(
                            candidate=candidate_profile,
                            title=request.POST.get('title', 'My Resume'),
                            file=file,
                            file_type=ext,
                            file_size=file.size,
                            is_default=is_default,
                        )
                        messages.success(request, 'Resume uploaded!')

        elif action == 'set_default':
            resume_id = request.POST.get('resume_id')
            resumes.update(is_default=False)
            resumes.filter(id=resume_id).update(is_default=True)
            messages.success(request, 'Default resume updated.')

        elif action == 'delete':
            resume_id = request.POST.get('resume_id')
            resume = resumes.filter(id=resume_id).first()
            if resume:
                resume.file.delete(save=False)
                resume.delete()
                messages.success(request, 'Resume deleted.')

        return redirect('candidates:resume')

    return render(request, 'candidates/resume.html', {'resumes': resumes})


@login_required
@candidate_required
def add_skill(request):
    candidate_profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        skill_name = request.POST.get('skill_name', '').strip()
        proficiency = request.POST.get('proficiency', 'intermediate')
        years = request.POST.get('years_of_experience', 0)
        if skill_name:
            CandidateSkill.objects.get_or_create(
                candidate=candidate_profile, skill_name=skill_name,
                defaults={'proficiency': proficiency, 'years_of_experience': int(years)}
            )
            messages.success(request, 'Skill added!')
        return redirect('candidates:profile')
    return render(request, 'candidates/add_skill.html')


@login_required
@candidate_required
def delete_skill(request, skill_id):
    profile = get_or_create_profile(request.user)
    CandidateSkill.objects.filter(id=skill_id, candidate=profile).delete()
    return redirect('candidates:profile')


@login_required
@candidate_required
def add_education(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        data = request.POST
        Education.objects.create(
            candidate=profile,
            degree=data.get('degree', ''),
            field_of_study=data.get('field_of_study', ''),
            institution=data.get('institution', ''),
            start_year=int(data.get('start_year', 2020)),
            end_year=data.get('end_year') or None,
            percentage=data.get('percentage') or None,
            is_current=bool(data.get('is_current')),
        )
        messages.success(request, 'Education added!')
        return redirect('candidates:profile')
    return render(request, 'candidates/add_education.html')


@login_required
@candidate_required
def edit_education(request, edu_id):
    profile = get_or_create_profile(request.user)
    edu = get_object_or_404(Education, id=edu_id, candidate=profile)
    if request.method == 'POST':
        data = request.POST
        edu.degree = data.get('degree', edu.degree)
        edu.field_of_study = data.get('field_of_study', edu.field_of_study)
        edu.institution = data.get('institution', edu.institution)
        edu.start_year = int(data.get('start_year', edu.start_year))
        edu.end_year = data.get('end_year') or None
        edu.percentage = data.get('percentage') or None
        edu.is_current = bool(data.get('is_current'))
        edu.save()
        messages.success(request, 'Education updated!')
        return redirect('candidates:profile')
    return render(request, 'candidates/add_education.html', {'edu': edu})


@login_required
@candidate_required
def delete_education(request, edu_id):
    profile = get_or_create_profile(request.user)
    Education.objects.filter(id=edu_id, candidate=profile).delete()
    return redirect('candidates:profile')


@login_required
@candidate_required
def add_experience(request):
    profile = get_or_create_profile(request.user)
    if request.method == 'POST':
        data = request.POST
        WorkExperience.objects.create(
            candidate=profile,
            company_name=data.get('company_name', ''),
            designation=data.get('designation', ''),
            location=data.get('location', ''),
            start_date=data.get('start_date'),
            end_date=data.get('end_date') or None,
            is_current=bool(data.get('is_current')),
            description=data.get('description', ''),
        )
        messages.success(request, 'Experience added!')
        return redirect('candidates:profile')
    return render(request, 'candidates/add_experience.html')


@login_required
@candidate_required
def edit_experience(request, exp_id):
    profile = get_or_create_profile(request.user)
    exp = get_object_or_404(WorkExperience, id=exp_id, candidate=profile)
    if request.method == 'POST':
        data = request.POST
        exp.company_name = data.get('company_name', exp.company_name)
        exp.designation = data.get('designation', exp.designation)
        exp.location = data.get('location', exp.location)
        exp.start_date = data.get('start_date', exp.start_date)
        exp.end_date = data.get('end_date') or None
        exp.is_current = bool(data.get('is_current'))
        exp.description = data.get('description', exp.description)
        exp.save()
        messages.success(request, 'Experience updated!')
        return redirect('candidates:profile')
    return render(request, 'candidates/add_experience.html', {'exp': exp})


@login_required
@candidate_required
def delete_experience(request, exp_id):
    profile = get_or_create_profile(request.user)
    WorkExperience.objects.filter(id=exp_id, candidate=profile).delete()
    return redirect('candidates:profile')


@login_required
@candidate_required
def saved_jobs(request):
    profile = get_or_create_profile(request.user)
    saved = SavedJob.objects.filter(candidate=profile).select_related('job', 'job__company')
    return render(request, 'candidates/saved_jobs.html', {'saved_jobs': saved})
