from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Company


def company_list(request):
    companies = Company.objects.filter(is_active=True)
    q = request.GET.get('q', '')
    industry = request.GET.get('industry', '')
    if q:
        companies = companies.filter(name__icontains=q)
    if industry:
        companies = companies.filter(industry__icontains=industry)
    return render(request, 'companies/list.html', {'companies': companies})


def company_detail(request, slug):
    company = get_object_or_404(Company, slug=slug, is_active=True)
    jobs = company.jobs.filter(is_active=True, is_approved=True)
    return render(request, 'companies/detail.html', {'company': company, 'jobs': jobs})


@login_required
def my_company(request):
    if not request.user.is_recruiter:
        return redirect('dashboard:index')
    companies = Company.objects.filter(recruiter=request.user)
    return render(request, 'companies/my_company.html', {'companies': companies})


@login_required
def create_company(request):
    if not request.user.is_recruiter:
        return redirect('dashboard:index')
    if request.method == 'POST':
        data = request.POST
        name = data.get('name', '').strip()
        if not name:
            messages.error(request, 'Company name is required.')
            return redirect('companies:create')
        base_slug = slugify(name)
        slug = base_slug
        i = 1
        while Company.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"; i += 1
        company = Company.objects.create(
            recruiter=request.user,
            name=name,
            slug=slug,
            website=data.get('website', ''),
            industry=data.get('industry', ''),
            company_size=data.get('company_size', ''),
            description=data.get('description', ''),
            address=data.get('address', ''),
            city=data.get('city', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
        )
        if request.FILES.get('logo'):
            company.logo = request.FILES['logo']
            company.save()
        messages.success(request, 'Company profile created!')
        return redirect('companies:my_company')
    return render(request, 'companies/create.html', {'size_choices': Company.SIZE_CHOICES})
