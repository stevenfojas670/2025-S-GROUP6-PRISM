"""Views for the Courses app with enhanced filtering, ordering, search, and pagination."""

from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from prism_backend.mixins import CachedViewMixin
from rest_framework.request import Request

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

    def get_queryset(self):
        """
        - Extending the functionality of the get_queryset to retrieve courses by semester id
        """
        # Just gets the queryset defined at the top queryset = CourseInstances.objects.all()
        queryset = super().get_queryset()

        # Storing the HTTP Request sent from the client
        request = self.request

        # Retrieving the semester_id from the request
        semester_id = request.query_params.get("semester_id")

        # Need to check if the user is logged in by checking if the professor id is in the jwt token
        try:
            professor_id = request.user.professors.id
        except Professors.DoesNotExist:
            return queryset.none()  # Not a professor

        # We need to query all courses by professor id
        # Then we need to determine which courses have the semester id we passed
        if semester_id:
            return queryset.filter(
                professor_id=professor_id, semester_id=semester_id
            ).distinct()


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

    def get_queryset(self):
        """
        Returns semesters taught by a professor.

        - If `semester_id` is provided, return that semester (only if taught by the professor).
        - If not, return all semesters the professor has taught in.
        """
        queryset = super().get_queryset()
        request = self.request
        semester_id = request.query_params.get("semester_id")

        # Determine professor ID from query param or authenticated user
        professor_id = request.query_params.get("professor_id")
        if not professor_id:
            try:
                professor_id = request.user.professors.id
            except Professors.DoesNotExist:
                return queryset.none()  # Not a professor

        if not professor_id:
            return queryset.none()  # No professor context

        # If a specific semester ID is passed, return that one if linked to this professor
        if semester_id:
            return queryset.filter(
                id=semester_id, courseinstances__professor__id=professor_id
            ).distinct()

        # Otherwise return all semesters the professor has taught in
        return queryset.filter(courseinstances__professor__id=professor_id).distinct()


class CourseAssignmentCollaborationViewSet(viewsets.ModelViewSet, CachedViewMixin):
    """ViewSet for handling CourseAssignmentCollaboration entries."""

    queryset = CourseAssignmentCollaboration.objects.all()
    serializer_class = CourseAssignmentCollaborationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["assignment", "course_instance"]
    ordering_fields = ["assignment", "course_instance"]
    ordering = ["assignment"]
    search_fields = []


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
