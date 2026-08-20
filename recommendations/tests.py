from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from students.models import StudentProfile
from recruiters.models import Company
from opportunities.models import Opportunity
from recommendations.services import calculate_opportunity_match, get_recommendations_for_student


class RecommendationEngineTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test AI', verification_status=Company.VerificationStatus.VERIFIED)
        self.recruiter = User.objects.create_user(
            username='r@example.com', email='r@example.com', password='Password123!', role=User.Role.RECRUITER
        )

        self.student_user = User.objects.create_user(
            username='s@example.com', email='s@example.com', password='Password123!', role=User.Role.STUDENT
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            college='NIT Trichy',
            degree='B.Tech',
            department='Computer Science',
            graduation_year=2025,
            cgpa=Decimal('8.50'),
            skills='Python, Django, PostgreSQL, Docker',
            preferred_role='Full Stack Developer',
            preferred_location='Bangalore'
        )

    def test_high_compatibility_match(self):
        # Opportunity that perfectly matches student
        perfect_opp = Opportunity.objects.create(
            recruiter=self.recruiter,
            company=self.company,
            title='Full Stack Developer Intern',
            job_role='Full Stack Developer',
            description='Django role',
            required_skills='Python, Django, PostgreSQL',
            location='Bangalore',
            work_mode=Opportunity.WorkMode.HYBRID,
            min_cgpa=Decimal('7.50'),
            eligible_degree='B.Tech, M.Tech',
            eligible_department='Computer Science',
            graduation_year=2025,
            application_deadline=timezone.now().date() + timedelta(days=20),
            status=Opportunity.Status.APPROVED
        )

        breakdown = calculate_opportunity_match(self.student_profile, perfect_opp)
        self.assertGreaterEqual(breakdown['score'], 85)
        self.assertTrue(breakdown['dept_match'])
        self.assertTrue(breakdown['degree_match'])
        self.assertTrue(breakdown['cgpa_eligible'])
        self.assertEqual(len(breakdown['matched_skills']), 3)

    def test_low_compatibility_match_on_unrelated_field(self):
        # Opportunity in mechanical field with different skills
        unrelated_opp = Opportunity.objects.create(
            recruiter=self.recruiter,
            company=self.company,
            title='Automotive Thermal Engineer',
            job_role='Thermal Engineer',
            description='CAD design',
            required_skills='AutoCAD, SolidWorks, Thermodynamics',
            location='Pune',
            work_mode=Opportunity.WorkMode.ON_SITE,
            min_cgpa=Decimal('9.00'), # Higher than student CGPA
            eligible_degree='B.Tech',
            eligible_department='Mechanical Engineering',
            graduation_year=2024,
            application_deadline=timezone.now().date() + timedelta(days=20),
            status=Opportunity.Status.APPROVED
        )

        breakdown = calculate_opportunity_match(self.student_profile, unrelated_opp)
        self.assertLess(breakdown['score'], 40)
        self.assertFalse(breakdown['dept_match'])
        self.assertFalse(breakdown['cgpa_eligible'])
        self.assertEqual(len(breakdown['matched_skills']), 0)
