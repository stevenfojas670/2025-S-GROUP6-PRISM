"""Assignments Views with Enhanced Filtering, Ordering, and Search
Capabilities."""

from assignments import serializers
from assignments import models
from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter, SearchFilter

# below imports are for filtering / querying
from rest_framework.permissions import IsAuthenticated
from assignments.models import FlaggedSubmission
from assignments.serializers import FlaggedSubmissionSerializer
from users.permissions import is_admin

# from courses.models import ProfessorClassSection


class StudentVS(viewsets.ModelViewSet):
    """StudentVS is a ModelViewSet for managing Student objects.

    This viewset provides CRUD operations for the Student model and supports
    filtering, ordering, and searching functionalities.

    Attributes:
        queryset (QuerySet): A queryset containing all Student objects.
        serializer_class (Serializer): The serializer class used for Student objects.
        filter_backends (list): A list of filter backends used for filtering, ordering, and searching.
        filterset_fields (dict): Specifies the fields that can be filtered and their lookup types.
            - "id": Supports "exact" lookup.
            - "first_name": Supports "exact" and "icontains" lookups.
        ordering_fields (list): Specifies the fields that can be used for ordering.
            - "id"
            - "first_name"
        ordering (list): Specifies the default ordering for the queryset.
            - "first_name"
        search_fields (list): Specifies the fields that can be searched.
            - "first_name"
    """

    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {"id": ["exact"], "first_name": ["exact", "icontains"]}
    ordering_fields = ["id", "first_name"]
    ordering = ["first_name"]
    search_fields = ["first_name"]


class FlaggedStudentVS(viewsets.ModelViewSet):
    """FlaggedStudentVS is a ModelViewSet for managing FlaggedStudent objects.

    This viewset provides CRUD operations and supports filtering, ordering,
    and searching functionality for FlaggedStudent objects.

    Attributes:
        queryset (QuerySet): The queryset containing all FlaggedStudent objects.
        serializer_class (Serializer): The serializer class used for FlaggedStudent objects.
        filter_backends (list): A list of filter backends used for filtering, ordering, and searching.
        filterset_fields (dict): A dictionary defining the fields that can be filtered and their lookup types.
            - "professor__id": Supports "exact" lookup.
            - "times_over_threshold": Supports "exact", "gte", and "lte" lookups.
        ordering_fields (list): A list of fields that can be used for ordering results.
            - "professor__user__first_name"
            - "times_over_threshold"
        ordering (list): The default ordering applied to the results.
            - "times_over_threshold"
    """

    queryset = models.FlaggedStudent.objects.all()
    serializer_class = serializers.FlaggedStudentSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {
        "professor__id": ["exact"],
        "times_over_threshold": ["exact", "gte", "lte"],
    }
    ordering_fields = ["professor__user__first_name", "times_over_threshold"]
    ordering = ["times_over_threshold"]


class AssignmentVS(viewsets.ModelViewSet):
    """AssignmentVS is a viewset for managing Assignment objects.

    This viewset provides CRUD operations for the Assignment model and supports
    filtering, ordering, and searching functionalities.

    Attributes:
        queryset (QuerySet): The base queryset for retrieving Assignment objects.
        serializer_class (Serializer): The serializer class used for Assignment objects.
        filter_backends (list): A list of filter backends used for filtering, ordering, and searching.
        filterset_fields (dict): Fields available for filtering. Supports exact and case-insensitive contains (icontains) lookups.
            - professor__id: Filters by the exact ID of the professor.
            - class_instance__name: Filters by the exact or partial (icontains) name of the class instance.
            - title: Filters by the exact or partial (icontains) title of the assignment.
            - assignment_number: Filters by the exact assignment number.
        ordering_fields (list): Fields available for ordering results.
            - professor__user__first_name: Orders by the professor's first name.
            - class_instance__name: Orders by the name of the class instance.
            - title: Orders by the title of the assignment.
            - assignment_number: Orders by the assignment number.
        ordering (list): Default ordering for the queryset. Orders by assignment_number.
        search_fields (list): Fields available for searching.
            - title: Searches within the title of the assignment.
            - class_instance__name: Searches within the name of the class instance.
            - professor__user__first_name: Searches within the professor's first name.
    """

    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {
        "professor__id": ["exact"],
        "class_instance__name": ["exact", "icontains"],
        "title": ["exact", "icontains"],
        "assignment_number": ["exact"],
    }
    ordering_fields = [
        "professor__user__first_name",
        "class_instance__name",
        "title",
        "assignment_number",
    ]
    ordering = ["assignment_number"]
    search_fields = [
        "title",
        "class_instance__name",
        "professor__user__first_name",
    ]


class SubmissionVS(viewsets.ModelViewSet):
    """SubmissionVS is a ModelViewSet that provides CRUD operations for the
    Submission model.

    Attributes:
        queryset (QuerySet): A queryset containing all Submission objects.
        serializer_class (Serializer): The serializer class used for Submission objects.
        filter_backends (list): A list of filter backends used for filtering, ordering, and searching.
        filterset_fields (dict): A dictionary defining the fields that can be filtered,
            including nested fields such as:
            - "student__id": Filter by exact student ID.
            - "professor__id": Filter by exact professor ID.
            - "flagged": Filter by exact flagged status.
            - "assignment__class_instance__name": Filter by exact or case-insensitive partial match of class instance name.
            - "assignment__title": Filter by exact or case-insensitive partial match of assignment title.
        ordering_fields (list): A list of fields that can be used for ordering results, including:
            - "student__first_name": Order by student's first name.
            - "professor__user__first_name": Order by professor's first name.
            - "flagged": Order by flagged status.
            - "assignment__class_instance__name": Order by class instance name.
            - "assignment__title": Order by assignment title.
        ordering (list): The default ordering applied to the results, which is by assignment title.
        search_fields (list): A list of fields that can be searched, including:
            - "assignment__title": Search by assignment title.
            - "assignment__class_instance__name": Search by class instance name.
    """

    queryset = models.Submission.objects.all()
    serializer_class = serializers.SubmissionSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {
        "student__id": ["exact"],
        "professor__id": ["exact"],
        "flagged": ["exact"],
        "assignment__class_instance__name": ["exact", "icontains"],
        "assignment__title": ["exact", "icontains"],
    }
    ordering_fields = [
        "student__first_name",
        "professor__user__first_name",
        "flagged",
        "assignment__class_instance__name",
        "assignment__title",
    ]
    ordering = ["assignment__title"]
    search_fields = ["assignment__title", "assignment__class_instance__name"]


class FlaggedSubmissionVS(viewsets.ModelViewSet):
    """FlaggedSubmissionVS is a ModelViewSet for managing flagged submissions.

    This viewset provides CRUD operations for the `FlaggedSubmission` model and
    supports filtering, ordering, and searching functionalities.

    Attributes:
        queryset (QuerySet): Retrieves all instances of the `FlaggedSubmission` model.
        serializer_class (Serializer): Specifies the serializer class for the `FlaggedSubmission` model.
        filter_backends (list): Defines the filtering, ordering, and searching backends.
        filterset_fields (dict): Specifies the fields available for filtering:
            - "submission__professor__id": Filter by professor ID (exact match).
            - "file_name": Filter by file name (exact match or contains).
            - "percentage": Filter by percentage (exact, greater than or equal to, less than or equal to).
        ordering_fields (list): Specifies the fields available for ordering:
            - "submission__professor__user__first_name": Order by professor's first name.
            - "file_name": Order by file name.
            - "percentage": Order by percentage.
        ordering (list): Default ordering applied to the queryset (descending by percentage).
        search_fields (list): Specifies the fields available for searching:
            - "file_name": Search by file name.
            - "submission__professor__user__first_name": Search by professor's first name.
    """

    queryset = models.FlaggedSubmission.objects.all()
    serializer_class = serializers.FlaggedSubmissionSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {
        "submission__professor__id": ["exact"],
        "file_name": ["exact", "icontains"],
        "percentage": ["exact", "gte", "lte"],
    }
    ordering_fields = [
        "submission__professor__user__first_name",
        "file_name",
        "percentage",
    ]
    ordering = ["-percentage"]
    search_fields = ["file_name", "submission__professor__user__first_name"]


class ConfirmedCheaterVS(viewsets.ModelViewSet):
    """ConfirmedCheaterVS is a ModelViewSet for managing ConfirmedCheater
    objects.

    This viewset provides CRUD operations and supports filtering, ordering,
    and searching on the ConfirmedCheater model.

    Attributes:
        queryset (QuerySet): Retrieves all ConfirmedCheater objects from the database.
        serializer_class (Serializer): Specifies the serializer for ConfirmedCheater objects.
        filter_backends (list): Defines the backends used for filtering, ordering, and searching.
        filterset_fields (dict): Specifies the fields available for filtering, including:
            - professor__id: Filter by professor ID (exact match).
            - confirmed_date: Filter by confirmed date (exact, greater than or equal to, less than or equal to).
            - threshold_used: Filter by threshold used (exact, greater than or equal to, less than or equal to).
        ordering_fields (list): Specifies the fields available for ordering, including:
            - professor__user__first_name: Order by the professor's first name.
            - confirmed_date: Order by the confirmed date.
            - threshold_used: Order by the threshold used.
        ordering (list): Default ordering applied to the queryset, sorted by confirmed_date.
    """

    queryset = models.ConfirmedCheater.objects.all()
    serializer_class = serializers.ConfirmedCheaterSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {
        "professor__id": ["exact"],
        "confirmed_date": ["exact", "gte", "lte"],
        "threshold_used": ["exact", "gte", "lte"],
    }
    ordering_fields = [
        "professor__user__first_name",
        "confirmed_date",
        "threshold_used",
    ]
    ordering = ["confirmed_date"]


# an extension of the flaggedSubmissionVS. It supports searching
# by file name and professor. Only lets a professor see their classes,
# flaggedSubmissionVS is more suitable to be used by an admin, since
# it shows data from all classes.
class PlagiarismReportViewSet(viewsets.ModelViewSet):
    """PlagiarismReportViewSet is a Django REST Framework (DRF) viewset that
    provides CRUD operations for flagged submissions related to plagiarism
    reports. It uses the FlaggedSubmissionSerializer to serialize data and
    applies various filters, ordering, and search capabilities.

    Attributes:
        serializer_class (Serializer): Specifies the serializer to be used for
            converting FlaggedSubmission model instances to JSON.
        permission_classes (list): Defines the permissions required to access this
            viewset. Only authenticated users are allowed.
        filter_backends (list): Specifies the filtering, ordering, and search
            backends to be used.
        filterset_fields (list): Defines the fields that can be used for filtering
            flagged submissions.
        ordering_fields (list): Specifies the fields that can be used for ordering
            the results.
        search_fields (list): Defines the fields that can be searched using the
            search functionality.

    Methods:
        get_queryset(self):
            Returns the queryset of flagged submissions based on the user's role.
            Admin users can view all flagged submissions, while professors can only
            view flagged submissions related to their own submissions.
    """

    # This lets DRF use FlaggedSubmissionSerializer to convert
    # FlaggedSubmission model instances into
    # JSON data before sending it in the API response.
    serializer_class = FlaggedSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = [
        "submission__assignment__class_instance_id",
        "submission__assignment__class_instance__semester",
        "submission__assignment__class_instance__profclassect__semester_id",
    ]
    ordering_fields = [
        "submission__created_at",
        "submission__professor__user__first_name",
        "file_name",
        "percentage",
    ]
    search_fields = ["file_name", "submission__professor__user__first_name"]

    def get_queryset(self):
        """Retrieves the queryset of flagged submissions based on the user's
        role.

        - If the user is an admin, all flagged submissions are returned.
        - If the user is a professor, only flagged submissions associated with
          the professor's submissions are returned.

        Returns:
            QuerySet: A queryset of `FlaggedSubmission` objects filtered based
            on the user's role.
        """
        user = self.request.user

        # Admins should see all flagged submissions. is_admin is
        # from users/permissions.py
        if is_admin(user):
            return FlaggedSubmission.objects.all()
        else:
            professor = user.user_professor
            return FlaggedSubmission.objects.filter(
                submission__professor=professor
            ).distinct()
