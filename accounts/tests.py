"""
JobPortal Unit Tests
Run: python manage.py test
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from jobs.models import Job, JobCategory
from companies.models import Company
from applications.models import Application
from candidates.models import CandidateProfile, Resume
from notifications.models import Notification

User = get_user_model()


# ─────────────────────────────────────────────
# Helper factories
# ─────────────────────────────────────────────
def make_candidate(email='candidate@test.com', password='TestPass123!'):
    return User.objects.create_user(
        email=email, password=password,
        first_name='Test', last_name='Candidate',
        role=User.CANDIDATE, is_verified=True,
    )

def make_recruiter(email='recruiter@test.com', password='TestPass123!'):
    return User.objects.create_user(
        email=email, password=password,
        first_name='Test', last_name='Recruiter',
        role=User.RECRUITER, is_verified=True,
    )

def make_company(recruiter):
    return Company.objects.create(
        recruiter=recruiter, name='Test Company',
        slug='test-company', is_verified=True,
    )

def make_job(recruiter, company, title='Python Developer'):
    cat, _ = JobCategory.objects.get_or_create(name='IT', defaults={'slug': 'it'})
    return Job.objects.create(
        recruiter=recruiter, company=company, category=cat,
        title=title, slug=f'python-developer-{Job.objects.count()}',
        description='Job description', location='Chennai',
        job_type='full_time', experience_required='1-3',
        is_active=True, is_approved=True,
    )


# ─────────────────────────────────────────────
# 1. User Model Tests
# ─────────────────────────────────────────────
class UserModelTest(TestCase):

    def test_create_candidate(self):
        user = make_candidate()
        self.assertEqual(user.role, User.CANDIDATE)
        self.assertTrue(user.is_candidate)
        self.assertFalse(user.is_recruiter)

    def test_create_recruiter(self):
        user = make_recruiter()
        self.assertEqual(user.role, User.RECRUITER)
        self.assertTrue(user.is_recruiter)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@test.com', password='Admin123!',
            first_name='Admin', last_name='User',
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_full_name(self):
        user = make_candidate()
        self.assertEqual(user.get_full_name(), 'Test Candidate')

    def test_email_unique(self):
        make_candidate()
        with self.assertRaises(Exception):
            make_candidate()  # duplicate email


# ─────────────────────────────────────────────
# 2. Authentication View Tests
# ─────────────────────────────────────────────
class AuthViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.candidate = make_candidate()
        self.recruiter = make_recruiter()

    def test_login_page_loads(self):
        res = self.client.get(reverse('accounts:login'))
        self.assertEqual(res.status_code, 200)

    def test_login_valid(self):
        res = self.client.post(reverse('accounts:login'), {
            'username': 'candidate@test.com',
            'password': 'TestPass123!',
        })
        self.assertRedirects(res, reverse('dashboard:index'))

    def test_login_invalid(self):
        res = self.client.post(reverse('accounts:login'), {
            'username': 'candidate@test.com',
            'password': 'WrongPass!',
        })
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Invalid')

    def test_logout(self):
        self.client.login(username='candidate@test.com', password='TestPass123!')
        res = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(res, reverse('accounts:login'))

    def test_register_candidate_page(self):
        res = self.client.get(reverse('accounts:register_candidate'))
        self.assertEqual(res.status_code, 200)

    def test_register_candidate_post(self):
        res = self.client.post(reverse('accounts:register_candidate'), {
            'first_name': 'New', 'last_name': 'User',
            'email': 'new@test.com', 'phone': '9999999999',
            'password': 'NewPass123!', 'confirm_password': 'NewPass123!',
        })
        self.assertTrue(User.objects.filter(email='new@test.com').exists())

    def test_register_duplicate_email(self):
        self.client.post(reverse('accounts:register_candidate'), {
            'first_name': 'A', 'last_name': 'B',
            'email': 'candidate@test.com',
            'password': 'TestPass123!', 'confirm_password': 'TestPass123!',
        })
        self.assertEqual(User.objects.filter(email='candidate@test.com').count(), 1)

    def test_protected_view_redirects_anonymous(self):
        res = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(res, reverse('accounts:login') + '?next=' + reverse('dashboard:index'))


# ─────────────────────────────────────────────
# 3. Job Model Tests
# ─────────────────────────────────────────────
class JobModelTest(TestCase):

    def setUp(self):
        self.recruiter = make_recruiter()
        self.company = make_company(self.recruiter)

    def test_create_job(self):
        job = make_job(self.recruiter, self.company)
        self.assertTrue(Job.objects.filter(title='Python Developer').exists())

    def test_salary_display_both(self):
        job = make_job(self.recruiter, self.company)
        job.min_salary = 500000
        job.max_salary = 800000
        job.is_salary_disclosed = True
        self.assertIn('500,000', job.salary_display)

    def test_salary_display_not_disclosed(self):
        job = make_job(self.recruiter, self.company)
        job.is_salary_disclosed = False
        self.assertEqual(job.salary_display, 'Not Disclosed')

    def test_job_expired(self):
        job = make_job(self.recruiter, self.company)
        job.application_deadline = timezone.now().date() - timedelta(days=1)
        self.assertTrue(job.is_expired)

    def test_job_not_expired(self):
        job = make_job(self.recruiter, self.company)
        job.application_deadline = timezone.now().date() + timedelta(days=10)
        self.assertFalse(job.is_expired)

    def test_job_str(self):
        job = make_job(self.recruiter, self.company)
        self.assertIn('Python Developer', str(job))


# ─────────────────────────────────────────────
# 4. Job View Tests
# ─────────────────────────────────────────────
class JobViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.candidate = make_candidate()
        self.recruiter = make_recruiter()
        self.company = make_company(self.recruiter)
        self.job = make_job(self.recruiter, self.company)

    def test_job_list_page(self):
        res = self.client.get(reverse('jobs:list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Python Developer')

    def test_job_detail_page(self):
        res = self.client.get(reverse('jobs:detail', args=[self.job.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.job.title)

    def test_job_list_search(self):
        res = self.client.get(reverse('jobs:list') + '?q=Python')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Python Developer')

    def test_job_list_no_match(self):
        res = self.client.get(reverse('jobs:list') + '?q=Java')
        self.assertNotContains(res, 'Python Developer')

    def test_post_job_requires_login(self):
        res = self.client.get(reverse('jobs:post'))
        self.assertEqual(res.status_code, 302)

    def test_post_job_requires_recruiter(self):
        self.client.login(username='candidate@test.com', password='TestPass123!')
        res = self.client.get(reverse('jobs:post'))
        self.assertEqual(res.status_code, 302)

    def test_post_job_as_recruiter(self):
        self.client.login(username='recruiter@test.com', password='TestPass123!')
        res = self.client.get(reverse('jobs:post'))
        # Should redirect to company creation if no company
        self.assertIn(res.status_code, [200, 302])


# ─────────────────────────────────────────────
# 5. Application Tests
# ─────────────────────────────────────────────
class ApplicationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.candidate = make_candidate()
        self.recruiter = make_recruiter()
        self.company = make_company(self.recruiter)
        self.job = make_job(self.recruiter, self.company)
        self.profile = CandidateProfile.objects.create(user=self.candidate)
        self.resume = Resume.objects.create(
            candidate=self.profile, title='My Resume',
            file='resumes/test.pdf', file_type='pdf',
            file_size=1024, is_default=True,
        )

    def test_apply_requires_login(self):
        res = self.client.get(reverse('applications:apply', args=[self.job.slug]))
        self.assertEqual(res.status_code, 302)

    def test_apply_page_loads_for_candidate(self):
        self.client.login(username='candidate@test.com', password='TestPass123!')
        res = self.client.get(reverse('applications:apply', args=[self.job.slug]))
        self.assertEqual(res.status_code, 200)

    def test_submit_application(self):
        self.client.login(username='candidate@test.com', password='TestPass123!')
        res = self.client.post(reverse('applications:apply', args=[self.job.slug]), {
            'resume_id': self.resume.id,
            'cover_letter': 'I am very interested.',
        })
        self.assertTrue(Application.objects.filter(candidate=self.candidate, job=self.job).exists())

    def test_duplicate_application(self):
        Application.objects.create(candidate=self.candidate, job=self.job, status='applied')
        self.client.login(username='candidate@test.com', password='TestPass123!')
        res = self.client.post(reverse('applications:apply', args=[self.job.slug]), {
            'resume_id': self.resume.id,
        })
        self.assertEqual(Application.objects.filter(candidate=self.candidate, job=self.job).count(), 1)

    def test_my_applications_page(self):
        Application.objects.create(candidate=self.candidate, job=self.job, status='applied')
        self.client.login(username='candidate@test.com', password='TestPass123!')
        res = self.client.get(reverse('applications:my_applications'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Python Developer')

    def test_application_status_choices(self):
        statuses = [s[0] for s in Application.STATUS_CHOICES]
        self.assertIn('applied', statuses)
        self.assertIn('shortlisted', statuses)
        self.assertIn('selected', statuses)
        self.assertIn('rejected', statuses)

    def test_withdraw_application(self):
        app = Application.objects.create(candidate=self.candidate, job=self.job, status='applied')
        self.client.login(username='candidate@test.com', password='TestPass123!')
        self.client.get(reverse('applications:withdraw', args=[app.id]))
        app.refresh_from_db()
        self.assertEqual(app.status, 'withdrawn')


# ─────────────────────────────────────────────
# 6. Candidate Profile Tests
# ─────────────────────────────────────────────
class CandidateProfileTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.candidate = make_candidate()
        self.profile = CandidateProfile.objects.create(user=self.candidate)

    def test_profile_created(self):
        self.assertIsNotNone(self.profile)

    def test_profile_page_requires_login(self):
        res = self.client.get(reverse('candidates:profile'))
        self.assertEqual(res.status_code, 302)

    def test_profile_page_loads(self):
        self.client.login(username='candidate@test.com', password='TestPass123!')
        res = self.client.get(reverse('candidates:profile'))
        self.assertEqual(res.status_code, 200)

    def test_profile_completion_zero(self):
        completion = self.profile.calculate_completion()
        self.assertIsInstance(completion, int)
        self.assertGreaterEqual(completion, 0)

    def test_add_skill(self):
        from candidates.models import CandidateSkill
        CandidateSkill.objects.create(
            candidate=self.profile, skill_name='Python',
            proficiency='expert', years_of_experience=3,
        )
        self.assertEqual(self.profile.skills.count(), 1)


# ─────────────────────────────────────────────
# 7. Notification Tests
# ─────────────────────────────────────────────
class NotificationTest(TestCase):

    def setUp(self):
        self.user = make_candidate()

    def test_create_notification(self):
        notif = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='You have a new notification',
            notification_type='general',
        )
        self.assertFalse(notif.is_read)
        self.assertEqual(str(notif), 'Test Notification → candidate@test.com')

    def test_mark_all_read(self):
        Notification.objects.create(recipient=self.user, title='N1', message='M1')
        Notification.objects.create(recipient=self.user, title='N2', message='M2')
        Notification.objects.filter(recipient=self.user).update(is_read=True)
        unread = Notification.objects.filter(recipient=self.user, is_read=False).count()
        self.assertEqual(unread, 0)


# ─────────────────────────────────────────────
# 8. Company Tests
# ─────────────────────────────────────────────
class CompanyTest(TestCase):

    def test_create_company(self):
        recruiter = make_recruiter()
        company = make_company(recruiter)
        self.assertEqual(company.name, 'Test Company')
        self.assertEqual(company.recruiter, recruiter)

    def test_company_list_page(self):
        client = Client()
        res = client.get(reverse('companies:list'))
        self.assertEqual(res.status_code, 200)

    def test_company_detail_page(self):
        recruiter = make_recruiter()
        company = make_company(recruiter)
        client = Client()
        res = client.get(reverse('companies:detail', args=[company.slug]))
        self.assertEqual(res.status_code, 200)
