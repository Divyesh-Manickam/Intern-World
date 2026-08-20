from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from recruiters.models import Company, RecruiterProfile
from opportunities.models import Opportunity


class OpportunityWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create verified company & recruiter
        self.company = Company.objects.create(
            name='Alpha Technologies',
            industry='Software',
            verification_status=Company.VerificationStatus.VERIFIED
        )
        self.recruiter = User.objects.create_user(
            username='rec@example.com',
            email='rec@example.com',
            password='Password123!',
            role=User.Role.RECRUITER
        )
        RecruiterProfile.objects.create(user=self.recruiter, company=self.company)

    def test_opportunity_creation_auto_approves_for_verified_company(self):
        self.client.login(username='rec@example.com', password='Password123!')
        
        response = self.client.post(reverse('opportunities:create'), {
            'title': 'Django Backend Intern',
            'opportunity_type': 'INTERNSHIP',
            'job_role': 'Backend Developer',
            'description': 'Building Django applications.',
            'responsibilities': 'API design.',
            'requirements': 'Python experience.',
            'required_skills': 'Python, Django, PostgreSQL',
            'location': 'Bangalore',
            'work_mode': 'REMOTE',
            'stipend': '₹30,000 / month',
            'salary': '',
            'duration': '6 Months',
            'min_cgpa': '7.00',
            'eligible_degree': 'All Degrees',
            'eligible_department': 'All Departments',
            'graduation_year': 2025,
            'openings_count': 2,
            'application_deadline': (timezone.now().date() + timedelta(days=20)).isoformat(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Opportunity.objects.filter(title='Django Backend Intern').exists())
        opp = Opportunity.objects.get(title='Django Backend Intern')
        self.assertEqual(opp.status, Opportunity.Status.APPROVED)

    def test_public_catalog_filters_closed_or_pending(self):
        # Approved Opportunity
        opp_approved = Opportunity.objects.create(
            recruiter=self.recruiter,
            company=self.company,
            title='Public Approved Job',
            job_role='Engineer',
            description='Active',
            required_skills='Python',
            location='Bangalore',
            application_deadline=timezone.now().date() + timedelta(days=10),
            status=Opportunity.Status.APPROVED
        )

        # Pending Opportunity
        opp_pending = Opportunity.objects.create(
            recruiter=self.recruiter,
            company=self.company,
            title='Hidden Pending Job',
            job_role='Engineer',
            description='Pending',
            required_skills='Python',
            location='Bangalore',
            application_deadline=timezone.now().date() + timedelta(days=10),
            status=Opportunity.Status.PENDING
        )

        response = self.client.get(reverse('opportunities:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Approved Job')
        self.assertNotContains(response, 'Hidden Pending Job')
