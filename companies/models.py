from django.db import models
from django.conf import settings


class Company(models.Model):
    SIZE_CHOICES = [
        ('1-10', '1-10 Employees'),
        ('11-50', '11-50 Employees'),
        ('51-200', '51-200 Employees'),
        ('201-500', '201-500 Employees'),
        ('501-1000', '501-1000 Employees'),
        ('1001-5000', '1001-5000 Employees'),
        ('5000+', '5000+ Employees'),
    ]

    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name
