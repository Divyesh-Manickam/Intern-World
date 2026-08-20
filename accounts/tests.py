from django.test import TestCase, Client
from django.urls import reverse
from .models import User
from students.models import StudentProfile
from recruiters.models import Company, RecruiterProfile


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_student_registration_creates_profile(self):
        response = self.client.post(reverse('accounts:register_student'), {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'newstudent@example.com',
            'phone': '+91 9999999999',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'college': 'Test College of Engineering',
            'degree': 'B.Tech',
            'department': 'Computer Science',
            'graduation_year': 2025,
            'cgpa': '8.50',
            'skills': 'Python, Django, PostgreSQL',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newstudent@example.com').exists())
        user = User.objects.get(email='newstudent@example.com')
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(hasattr(user, 'student_profile'))
        self.assertEqual(user.student_profile.college, 'Test College of Engineering')

    def test_recruiter_registration_creates_company(self):
        response = self.client.post(reverse('accounts:register_recruiter'), {
            'first_name': 'Test',
            'last_name': 'Recruiter',
            'email': 'newrecruiter@example.com',
            'phone': '+91 8888888888',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'company_name': 'Novel AI Labs',
            'company_description': 'AI R&D startup.',
            'company_website': 'https://novelai.example.com',
            'industry': 'Artificial Intelligence',
            'location': 'Bangalore',
            'designation': 'Hiring Lead',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newrecruiter@example.com').exists())
        user = User.objects.get(email='newrecruiter@example.com')
        self.assertEqual(user.role, User.Role.RECRUITER)
        self.assertTrue(hasattr(user, 'recruiter_profile'))
        self.assertEqual(user.recruiter_profile.company.name, 'Novel AI Labs')
        self.assertEqual(user.recruiter_profile.company.verification_status, Company.VerificationStatus.PENDING)

    def test_role_based_access_control(self):
        # Create student user
        student = User.objects.create_user(
            username='s1@example.com',
            email='s1@example.com',
            password='Password123!',
            role=User.Role.STUDENT
        )
        StudentProfile.objects.create(user=student)

        # Log in as student
        self.client.login(username='s1@example.com', password='Password123!')

        # Student cannot access recruiter applicant management
        response = self.client.get(reverse('recruiters:applicants'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:dashboard_redirect'))

        # Student cannot access admin center
        response = self.client.get(reverse('analytics:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:dashboard_redirect'))
