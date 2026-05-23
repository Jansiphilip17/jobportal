from django.db import models
from django.conf import settings


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class')
    job_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_categories'
        verbose_name_plural = 'Job Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
        ('freelance', 'Freelance'),
    ]
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('0-1', '0-1 Years'),
        ('1-3', '1-3 Years'),
        ('3-5', '3-5 Years'),
        ('5-10', '5-10 Years'),
        ('10+', '10+ Years'),
    ]

    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    benefits = models.TextField(blank=True)

    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_required = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, default='fresher')
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)

    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='INR')
    is_salary_disclosed = models.BooleanField(default=True)

    num_openings = models.IntegerField(default=1)
    application_deadline = models.DateField(null=True, blank=True)

    skills_required = models.ManyToManyField('JobSkill', through='JobSkillMapping', blank=True)

    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    applications_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title', 'location']),
            models.Index(fields=['is_active', 'is_approved']),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company.name}"

    @property
    def salary_display(self):
        if not self.is_salary_disclosed:
            return "Not Disclosed"
        if self.min_salary and self.max_salary:
            return f"₹{self.min_salary:,.0f} - ₹{self.max_salary:,.0f}"
        if self.min_salary:
            return f"₹{self.min_salary:,.0f}+"
        return "Not Disclosed"

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.application_deadline:
            return self.application_deadline < timezone.now().date()
        return False


class JobSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'job_skills'

    def __str__(self):
        return self.name


class JobSkillMapping(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(JobSkill, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=True)

    class Meta:
        db_table = 'job_skill_mappings'
        unique_together = ['job', 'skill']
