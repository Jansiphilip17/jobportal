from django import forms
from .models import Job, JobCategory


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'category', 'job_type',
            'experience_required', 'location', 'is_remote',
            'description', 'responsibilities', 'requirements', 'benefits',
            'min_salary', 'max_salary', 'is_salary_disclosed',
            'num_openings', 'application_deadline',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Senior Python Developer'
            }),
            'company': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'experience_required': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Chennai, Bangalore or Remote'
            }),
            'is_remote': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the role and what the candidate will do...'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '- Develop and maintain applications\n- Write clean code\n...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '- 2+ years experience\n- Strong Python skills\n...'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '- Health insurance\n- Remote work\n- Annual bonus\n...'
            }),
            'min_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 500000'
            }),
            'max_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 1000000'
            }),
            'is_salary_disclosed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'num_openings': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, recruiter=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show companies belonging to this recruiter
        if recruiter:
            from companies.models import Company
            self.fields['company'].queryset = Company.objects.filter(recruiter=recruiter)
        self.fields['category'].queryset = JobCategory.objects.all()
        self.fields['category'].empty_label = 'Select Category'
        self.fields['company'].empty_label  = 'Select Company'
        # Make some fields optional
        self.fields['responsibilities'].required = False
        self.fields['requirements'].required      = False
        self.fields['benefits'].required          = False
        self.fields['min_salary'].required        = False
        self.fields['max_salary'].required        = False
        self.fields['application_deadline'].required = False
        self.fields['category'].required          = False