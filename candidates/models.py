from django.db import models
from django.conf import settings


class CandidateProfile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('P', 'Prefer not to say')]
    NOTICE_PERIOD_CHOICES = [
        ('immediate', 'Immediate'),
        ('15', '15 Days'),
        ('30', '1 Month'),
        ('60', '2 Months'),
        ('90', '3 Months'),
        ('more', 'More than 3 Months'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate_profile')
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    # Professional details
    headline = models.CharField(max_length=255, blank=True, help_text='e.g., Senior Python Developer')
    summary = models.TextField(blank=True, help_text='About yourself')
    current_company = models.CharField(max_length=200, blank=True)
    current_designation = models.CharField(max_length=200, blank=True)
    total_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0, help_text='Years')
    current_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expected_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notice_period = models.CharField(max_length=20, choices=NOTICE_PERIOD_CHOICES, blank=True)
    preferred_locations = models.CharField(max_length=500, blank=True, help_text='Comma-separated cities')

    # Social links
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    # Meta
    is_profile_visible = models.BooleanField(default=True)
    profile_completion = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate_profiles'
        verbose_name = 'Candidate Profile'

    def __str__(self):
        return f"{self.user.get_full_name()} - Profile"

    def calculate_completion(self):
        fields = [self.dob, self.gender, self.address, self.headline, self.summary,
                  self.current_company, self.total_experience, self.expected_salary, self.notice_period]
        filled = sum(1 for f in fields if f)
        # Check skills and education
        has_skills = self.skills.exists()
        has_education = self.education.exists()
        has_resume = self.resumes.exists()
        total = len(fields) + 3
        completion = (filled + (1 if has_skills else 0) + (1 if has_education else 0) + (1 if has_resume else 0)) / total * 100
        return int(completion)


class Education(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    institution = models.CharField(max_length=300)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'education'
        ordering = ['-end_year', '-start_year']

    def __str__(self):
        return f"{self.degree} from {self.institution}"


class CandidateSkill(models.Model):
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='intermediate')
    years_of_experience = models.IntegerField(default=0)

    class Meta:
        db_table = 'candidate_skills'
        unique_together = ['candidate', 'skill_name']

    def __str__(self):
        return f"{self.skill_name} ({self.proficiency})"


class WorkExperience(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='work_experience')
    company_name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'work_experience'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.designation} at {self.company_name}"


class Resume(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200, default='My Resume')
    file = models.FileField(upload_to='resumes/')
    file_type = models.CharField(max_length=10)
    file_size = models.IntegerField(help_text='Size in bytes')
    is_default = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resumes'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.candidate.user.get_full_name()}"


class SavedJob(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_jobs'
        unique_together = ['candidate', 'job']

    def __str__(self):
        return f"{self.candidate.user.get_full_name()} saved {self.job.title}"
