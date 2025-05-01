"""Views for the Courses app with enhanced filtering, ordering, search, and pagination."""

from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from prism_backend.mixins import CachedViewMixin
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import (
    CourseCatalog,
    CourseInstances,
    Semester,
    Students,
    StudentEnrollments,
    Professors,
    ProfessorEnrollments,
    TeachingAssistants,
    TeachingAssistantEnrollments,
)
from .serializers import (
    CourseCatalogSerializer,
    CourseInstancesSerializer,
    SemesterSerializer,
    StudentsSerializer,
    StudentEnrollmentsSerializer,
    ProfessorsSerializer,
    ProfessorEnrollmentsSerializer,
    TeachingAssistantsSerializer,
    TeachingAssistantEnrollmentsSerializer,
)
from .pagination import StandardResultsSetPagination


class CourseCatalogViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling CourseCatalog entries."""

    queryset = CourseCatalog.objects.all()
    serializer_class = CourseCatalogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["subject", "catalog_number", "course_title"]
    ordering_fields = ["catalog_number", "course_title"]
    ordering = ["catalog_number"]
    search_fields = ["name", "course_title"]


class CourseInstancesViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling CourseInstances entries."""

    queryset = CourseInstances.objects.all()
    course_catalog = CourseCatalogSerializer()
    serializer_class = CourseInstancesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["section_number", "canvas_course_id", "professor", "semester"]
    ordering_fields = ["section_number"]
    ordering = ["section_number"]
    search_fields = ["course_catalog__course_title"]

    @action(detail=False, methods=["get"], url_path="get-courses-by-semesters")
    def get_courses(self, request: Request) -> Response:
        """
        Returns all courses for the current logged-in professor for a given semester.
        If the user is a superuser, returns all matching courses for the semester.

        Example: /courseinstances/get-courses/?uid=3&semester=6
        """
        user_id = request.query_params.get("uid")
        semester_id = request.query_params.get("semester")

        if not user_id or not semester_id:
            return Response(
                {"detail": "Both 'uid' and 'semester' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            semester = Semester.objects.get(id=semester_id)
        except Semester.DoesNotExist:
            return Response(
                {"detail": "Semester not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if user.is_superuser:
            course_instances = CourseInstances.objects.filter(
                semester=semester
            ).select_related("semester", "professor", "course_catalog")
        else:
            try:
                professor = Professors.objects.get(user=user)
            except Professors.DoesNotExist:
                return Response(
                    {"detail": "User is not a professor."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            course_instances = CourseInstances.objects.filter(
                professor=professor, semester=semester
            ).select_related("semester", "professor", "course_catalog")

        # Apply pagination
        page = self.paginate_queryset(course_instances)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(course_instances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="get-all-courses")
    def get_all_courses(self, request: Request) -> Response:
        """
        Returns all courses for the current logged-in professor (across all semesters).
        If the user is a superuser, returns all courses.

        Example: /courseinstances/get-all-courses/?uid=3
        """
        user_id = request.query_params.get("uid")

        if not user_id:
            return Response(
                {"detail": "'uid' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if user.is_superuser:
            course_instances = CourseInstances.objects.all().select_related(
                "semester", "professor", "course_catalog"
            )
        else:
            try:
                professor = Professors.objects.get(user=user)
            except Professors.DoesNotExist:
                return Response(
                    {"detail": "User is not a professor."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            course_instances = CourseInstances.objects.filter(
                professor=professor
            ).select_related("semester", "professor", "course_catalog")

        # Apply pagination
        page = self.paginate_queryset(course_instances)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(course_instances, many=True)
        return Response(serializer.data)


class SemesterViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling Semester entries."""

    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["year", "term"]
    ordering_fields = ["year"]
    ordering = ["year"]
    search_fields = ["name", "term", "session"]

    @action(detail=False, methods=["get"], url_path="get-semesters")
    def get_semesters(self, request: Request) -> Response:
        """
        Returns all semesters for the current logged in professor.
        If the user is admin, then returns all semesters.

        Example Request: /semester/get-semesters/?uid=2
        """

        user_id = request.query_params.get("uid")
        if not user_id:
            return Response(
                {"detail": "Missing uid query parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Admins get all semesters
        if user.is_superuser:
            print("Is admin.")
            semesters = Semester.objects.all()
        else:
            try:
                professor = Professors.objects.get(user=user)
                course_instances = CourseInstances.objects.filter(
                    professor=professor
                ).select_related("semester")
                semester_ids = course_instances.values_list(
                    "semester_id", flat=True
                ).distinct()
                semesters = Semester.objects.filter(id__in=semester_ids)
            except Professors.DoesNotExist:
                return Response(
                    {"detail": "User is not a professor."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = self.get_serializer(semesters, many=True)
        return Response(serializer.data)


class StudentsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling Students entries."""

    queryset = Students.objects.all()
    serializer_class = StudentsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["email", "nshe_id"]
    ordering_fields = ["first_name", "last_name"]
    ordering = ["first_name"]
    search_fields = ["first_name", "last_name", "ace_id"]


class StudentEnrollmentsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling StudentEnrollments entries."""

    queryset = StudentEnrollments.objects.all()
    serializer_class = StudentEnrollmentsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["student", "course_instance"]
    ordering_fields = ["student"]
    ordering = ["student"]
    search_fields = []


class ProfessorsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling Professors entries."""

    queryset = Professors.objects.all()
    serializer_class = ProfessorsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["user"]
    ordering_fields = ["user"]
    ordering = ["user"]
    search_fields = ["user__username"]


class ProfessorEnrollmentsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling ProfessorEnrollments entries."""

    queryset = ProfessorEnrollments.objects.all()
    serializer_class = ProfessorEnrollmentsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["professor", "course_instance"]
    ordering_fields = ["professor"]
    ordering = ["professor"]
    search_fields = []


class TeachingAssistantsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling TeachingAssistants entries."""

    queryset = TeachingAssistants.objects.all()
    serializer_class = TeachingAssistantsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["user"]
    ordering_fields = ["user"]
    ordering = ["user"]
    search_fields = ["user__username"]


class TeachingAssistantEnrollmentsViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling TeachingAssistantEnrollments entries."""

    queryset = TeachingAssistantEnrollments.objects.all()
    serializer_class = TeachingAssistantEnrollmentsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["teaching_assistant", "course_instance"]
    ordering_fields = ["teaching_assistant"]
    ordering = ["teaching_assistant"]
    search_fields = []
