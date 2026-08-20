from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from students.models import StudentProfile
from recruiters.models import Company, RecruiterProfile
from opportunities.models import Opportunity


class ApiEndpointsTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='API Tech', verification_status=Company.VerificationStatus.VERIFIED)
        self.recruiter = User.objects.create_user(
            username='rec_api@example.com', email='rec_api@example.com', password='Password123!', role=User.Role.RECRUITER
        )
        RecruiterProfile.objects.create(user=self.recruiter, company=self.company)

        self.student = User.objects.create_user(
            username='stu_api@example.com', email='stu_api@example.com', password='Password123!', role=User.Role.STUDENT
        )
        self.profile = StudentProfile.objects.create(
            user=self.student,
            college='NITK Surathkal',
            degree='B.Tech',
            department='Computer Science',
            graduation_year=2025,
            cgpa=Decimal('8.70'),
            skills='Python, Django, React'
        )

        self.opportunity = Opportunity.objects.create(
            recruiter=self.recruiter,
            company=self.company,
            title='Backend Python Engineer',
            job_role='Backend Engineer',
            description='API work',
            required_skills='Python, Django',
            location='Bangalore',
            application_deadline=timezone.now().date() + timedelta(days=15),
            status=Opportunity.Status.APPROVED
        )

    def test_get_opportunities_api(self):
        url = reverse('api_opportunity-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Backend Python Engineer')

    def test_student_recommendations_api(self):
        self.client.login(username='stu_api@example.com', password='Password123!')
        url = reverse('api_recommendations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.data)
        self.assertGreater(len(response.data['results']), 0)
        self.assertEqual(response.data['results'][0]['opportunity']['title'], 'Backend Python Engineer')
        self.assertGreater(response.data['results'][0]['match_score'], 50)
