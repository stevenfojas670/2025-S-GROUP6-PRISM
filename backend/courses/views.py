"""Views for the Courses app with enhanced filtering, ordering, search, and pagination."""

from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    CourseCatalog,
    CourseInstances,
    CoursesSemester,
    CourseAssignmentCollaboration,
    Students,
    StudentEnrollments,
    Professors,
    ProfessorEnrollments,
    TeachingAssistants,
    TeachingAssistantEnrollment,
)
from .serializers import (
    CourseCatalogSerializer,
    CourseInstancesSerializer,
    CoursesSemesterSerializer,
    CourseAssignmentCollaborationSerializer,
    StudentsSerializer,
    StudentEnrollmentsSerializer,
    ProfessorsSerializer,
    ProfessorEnrollmentsSerializer,
    TeachingAssistantsSerializer,
    TeachingAssistantEnrollmentSerializer,
)
from .pagination import StandardResultsSetPagination


class CourseCatalogViewSet(viewsets.ModelViewSet):
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
    search_fields = ["name", "course_title"]


class CourseInstancesViewSet(viewsets.ModelViewSet):
    """ViewSet for handling CourseInstances entries."""

    queryset = CourseInstances.objects.all()
    serializer_class = CourseInstancesSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["section_number", "canvas_course_id"]
    ordering_fields = ["section_number"]
    search_fields = ["course_catalog__course_title"]


class CoursesSemesterViewSet(viewsets.ModelViewSet):
    """ViewSet for handling CoursesSemester entries."""

    queryset = CoursesSemester.objects.all()
    serializer_class = CoursesSemesterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["year", "term"]
    ordering_fields = ["year"]
    search_fields = ["name", "term", "session"]


class CourseAssignmentCollaborationViewSet(viewsets.ModelViewSet):
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
    search_fields = []


class StudentsViewSet(viewsets.ModelViewSet):
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
    search_fields = ["first_name", "last_name", "ace_id"]


class StudentEnrollmentsViewSet(viewsets.ModelViewSet):
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
    search_fields = []


class ProfessorsViewSet(viewsets.ModelViewSet):
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
    search_fields = ["user__username"]


class ProfessorEnrollmentsViewSet(viewsets.ModelViewSet):
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
    search_fields = []


class TeachingAssistantsViewSet(viewsets.ModelViewSet):
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
    search_fields = ["user__username"]


class TeachingAssistantEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for handling TeachingAssistantEnrollment entries."""

    queryset = TeachingAssistantEnrollment.objects.all()
    serializer_class = TeachingAssistantEnrollmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["teaching_assistant", "course_instance"]
    ordering_fields = ["teaching_assistant"]
    search_fields = []
