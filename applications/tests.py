from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from students.models import StudentProfile
from recruiters.models import Company, RecruiterProfile
from opportunities.models import Opportunity
from applications.models import Application
from notifications.models import Notification


class ApplicationWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Recruiter & Company
        self.company = Company.objects.create(name='Acme Corp', verification_status=Company.VerificationStatus.VERIFIED)
        self.recruiter = User.objects.create_user(
            username='r1@example.com', email='r1@example.com', password='Password123!', role=User.Role.RECRUITER
        )
        RecruiterProfile.objects.create(user=self.recruiter, company=self.company)

        # Opportunity
        self.opportunity = Opportunity.objects.create(
            recruiter=self.recruiter,
            company=self.company,
            title='Software Engineer Intern',
            job_role='Software Engineer',
            description='Exciting role',
            required_skills='Python, Django',
            location='Bangalore',
            application_deadline=timezone.now().date() + timedelta(days=15),
            status=Opportunity.Status.APPROVED
        )

        # Student
        self.student = User.objects.create_user(
            username='s1@example.com', email='s1@example.com', password='Password123!', role=User.Role.STUDENT
        )
        self.profile = StudentProfile.objects.create(
            user=self.student,
            college='IIT Delhi',
            degree='B.Tech',
            department='Computer Science',
            graduation_year=2025,
            cgpa=Decimal('8.50'),
            skills='Python, Django, React',
            resume=ContentFile(b"%PDF-1.4\n%EOF", name="test_resume.pdf")
        )

    def test_student_can_apply_and_prevents_duplicate(self):
        self.client.login(username='s1@example.com', password='Password123!')

        # 1. First application submission
        response = self.client.post(reverse('applications:apply', kwargs={'pk': self.opportunity.id}), {
            'cover_letter': 'I am very interested in this role.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Application.objects.filter(student=self.student, opportunity=self.opportunity).exists())

        # Recruiter should receive notification
        self.assertTrue(Notification.objects.filter(user=self.recruiter).exists())

        # 2. Duplicate application attempt
        dup_response = self.client.post(reverse('applications:apply', kwargs={'pk': self.opportunity.id}), {
            'cover_letter': 'Applying again.'
        })
        self.assertEqual(dup_response.status_code, 302)
        # Count should still be 1
        self.assertEqual(Application.objects.filter(student=self.student, opportunity=self.opportunity).count(), 1)

    def test_recruiter_updates_candidate_status_triggers_notification(self):
        app = Application.objects.create(
            student=self.student,
            opportunity=self.opportunity,
            status=Application.Status.APPLIED
        )

        self.client.login(username='r1@example.com', password='Password123!')
        response = self.client.post(reverse('recruiters:update_status', kwargs={'pk': app.id}), {
            'status': Application.Status.SHORTLISTED,
            'recruiter_notes': 'Great match.'
        })
        self.assertEqual(response.status_code, 302)

        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.SHORTLISTED)
        self.assertEqual(app.recruiter_notes, 'Great match.')

        # Student should receive status update notification
        self.assertTrue(
            Notification.objects.filter(
                user=self.student,
                notification_type=Notification.NotificationType.APPLICATION,
                title__contains='Application Update'
            ).exists()
        )
