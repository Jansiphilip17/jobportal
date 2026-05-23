from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms

from .models import Interview
from applications.models import Application
from notifications.models import Notification


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interview_date', 'interview_time', 'duration_minutes', 'mode', 'round_type', 'meeting_link', 'notes']
        widgets = {
            'interview_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'interview_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'round_type': forms.Select(attrs={'class': 'form-select'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


@login_required
def schedule_interview(request, app_id):
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)

    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.scheduled_by = request.user
            interview.save()

            application.status = 'interview_scheduled'
            application.save()

            Notification.objects.create(
                recipient=application.candidate,
                title=f'Interview scheduled for {application.job.title}',
                message=f'Interview on {interview.interview_date} at {interview.interview_time}',
                notification_type='interview',
                link='/applications/my-applications/',
            )

            messages.success(request, 'Interview scheduled and candidate notified!')
            return redirect('recruiters:application_detail', app_id=app_id)
    else:
        form = InterviewForm()

    return render(request, 'interviews/schedule.html', {'form': form, 'application': application})
