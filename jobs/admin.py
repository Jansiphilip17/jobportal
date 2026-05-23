from django.contrib import admin
from .models import Job, JobCategory, JobSkill, JobSkillMapping

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'location', 'is_active', 'is_approved', 'created_at')
    list_filter = ('is_active', 'is_approved', 'job_type')
    search_fields = ('title', 'company__name', 'location')
    actions = ['approve_jobs']

    def approve_jobs(self, request, queryset):
        queryset.update(is_approved=True)
    approve_jobs.short_description = "Approve selected jobs"

admin.site.register(JobCategory)
admin.site.register(JobSkill)
