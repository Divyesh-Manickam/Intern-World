from rest_framework import serializers
from accounts.models import User
from students.models import StudentProfile, Project, Certification, Experience
from recruiters.models import Company, RecruiterProfile
from opportunities.models import Opportunity, SavedOpportunity
from applications.models import Application
from interviews.models import Interview
from notifications.models import Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'role']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'technologies', 'project_url', 'created_at']


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'issuing_organization', 'issue_date', 'credential_url']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'company', 'role', 'start_date', 'end_date', 'is_current', 'description']


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)
    completion_percentage = serializers.ReadOnlyField()

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'college', 'degree', 'department', 'graduation_year', 'cgpa',
            'skills', 'soft_skills', 'bio', 'preferred_location', 'preferred_role',
            'resume', 'github_url', 'linkedin_url', 'portfolio_url',
            'completion_percentage', 'projects', 'certifications', 'experiences'
        ]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'logo', 'description', 'website',
            'industry', 'location', 'verification_status', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'verification_status', 'created_at']


class RecruiterProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = RecruiterProfile
        fields = ['id', 'user', 'company', 'designation', 'department', 'created_at']


class OpportunitySerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    company_logo = serializers.SerializerMethodField()
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'title', 'company', 'company_name', 'company_logo', 'opportunity_type',
            'job_role', 'description', 'responsibilities', 'requirements', 'required_skills',
            'location', 'work_mode', 'stipend', 'salary', 'duration', 'min_cgpa',
            'eligible_degree', 'eligible_department', 'graduation_year', 'application_deadline',
            'openings_count', 'status', 'views_count', 'created_at'
        ]
        read_only_fields = ['id', 'views_count', 'created_at']

    def get_company_logo(self, obj):
        if obj.company and obj.company.logo:
            return obj.company.logo.url
        return None


class ApplicationSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only=True)
    student_name = serializers.ReadOnlyField(source='student.get_full_name')
    student_email = serializers.ReadOnlyField(source='student.email')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'opportunity', 'student_name', 'student_email', 'resume',
            'cover_letter', 'status', 'status_display', 'recruiter_notes',
            'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at']


class InterviewSerializer(serializers.ModelSerializer):
    opportunity_title = serializers.ReadOnlyField(source='application.opportunity.title')
    company_name = serializers.ReadOnlyField(source='application.opportunity.company.name')
    student_name = serializers.ReadOnlyField(source='student.get_full_name')
    interview_type_display = serializers.CharField(source='get_interview_type_display', read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'opportunity_title', 'company_name', 'student_name',
            'interview_date', 'interview_time', 'interview_type', 'interview_type_display',
            'meeting_link', 'location', 'instructions', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'link_url', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
