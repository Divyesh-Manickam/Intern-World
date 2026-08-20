from rest_framework import viewsets, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import User
from students.models import StudentProfile, Project, Certification, Experience
from recruiters.models import Company, RecruiterProfile
from opportunities.models import Opportunity, SavedOpportunity
from applications.models import Application
from interviews.models import Interview
from notifications.models import Notification
from recommendations.services import get_recommendations_for_student
from analytics.services import get_platform_overview_stats

from .serializers import (
    UserSerializer,
    StudentProfileSerializer,
    CompanySerializer,
    OpportunitySerializer,
    ApplicationSerializer,
    InterviewSerializer,
    NotificationSerializer
)


class CurrentUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class OpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Opportunity.objects.filter(
        status=Opportunity.Status.APPROVED,
        application_deadline__gte=timezone.now().date()
    ).select_related('company')
    serializer_class = OpportunitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['opportunity_type', 'work_mode']
    search_fields = ['title', 'job_role', 'company__name', 'required_skills', 'location']
    ordering_fields = ['created_at', 'application_deadline']


class StudentProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        serializer = StudentProfileSerializer(profile)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            return Application.objects.filter(student=user).select_related('opportunity__company')
        elif user.is_recruiter:
            return Application.objects.filter(opportunity__recruiter=user).select_related('opportunity__company', 'student')
        elif user.is_admin_user:
            return Application.objects.all().select_related('opportunity__company', 'student')
        return Application.objects.none()


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            return Interview.objects.filter(student=user).select_related('application__opportunity__company')
        elif user.is_recruiter:
            return Interview.objects.filter(recruiter=user).select_related('application__opportunity__company', 'student')
        elif user.is_admin_user:
            return Interview.objects.all()
        return Interview.objects.none()


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all marked as read'})


class RecommendationsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_student:
            return Response({'error': 'Recommendations are only available for students.'}, status=status.HTTP_403_FORBIDDEN)

        recs = get_recommendations_for_student(request.user, limit=10)
        results = []
        for opp, breakdown in recs:
            results.append({
                'opportunity': OpportunitySerializer(opp).data,
                'match_score': breakdown['score'],
                'reasons': breakdown['reasons'],
                'matched_skills': breakdown['matched_skills'],
                'missing_skills': breakdown['missing_skills'],
            })
        return Response({'results': results})


class AdminStatsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        stats = get_platform_overview_stats()
        return Response(stats)
