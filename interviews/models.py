from django.db import models
from django.conf import settings


class Interview(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('rescheduled', 'Rescheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    MODE_CHOICES = [
        ('in_person', 'In-Person'),
        ('phone', 'Phone Call'),
        ('video', 'Video Call'),
    ]
    ROUND_CHOICES = [
        ('screening', 'Screening'),
        ('technical', 'Technical Round'),
        ('hr', 'HR Round'),
        ('final', 'Final Round'),
        ('other', 'Other'),
    ]

    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='interviews')
    scheduled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_interviews')
    interview_date = models.DateField()
    interview_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='video')
    round_type = models.CharField(max_length=20, choices=ROUND_CHOICES, default='screening')
    location = models.CharField(max_length=300, blank=True, help_text='Physical location or video meeting link')
    meeting_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True, help_text='1-5 rating')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interviews'
        ordering = ['interview_date', 'interview_time']

    def __str__(self):
        return f"Interview for {self.application.candidate.get_full_name()} - {self.round_type}"
