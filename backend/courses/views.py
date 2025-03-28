"""Courses Views with Enhanced Filtering, Ordering, and Search Capabilities."""

from courses import serializers
from courses import models
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import rest_framework as filters


class ProfessorVS(viewsets.ModelViewSet):
    """
    A ViewSet for managing Professor objects.

    This ViewSet provides CRUD operations for the Professor model and supports
    filtering, ordering, and searching based on specific fields.

    Attributes:
        queryset (QuerySet): The queryset containing all Professor objects.
        serializer_class (Serializer): The serializer class used for Professor objects.
        filter_backends (list): A list of filter backends used for filtering, ordering, and searching.
        filterset_fields (dict): Fields that can be used for filtering. Supports exact and case-insensitive contains filters for `id` and `user__first_name`.
        ordering_fields (list): Fields that can be used for ordering results. Supports ordering by `user__first_name`.
        ordering (list): Default ordering for the queryset. Defaults to `user__first_name`.
        search_fields (list): Fields that can be used for search queries. Supports searching by `user__first_name`.
    """
    """Professor Model ViewSet."""

    queryset = models.Professor.objects.all()
    serializer_class = serializers.ProfessorSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {
        "id": ["exact"],
        "user__first_name": ["exact", "icontains"],
    }
    ordering_fields = ["user__first_name"]
    ordering = ["user__first_name"]
    search_fields = ["user__first_name"]


class SemesterVS(viewsets.ModelViewSet):
    """
    SemesterVS is a ModelViewSet for managing Semester objects.

    This viewset provides CRUD operations for the Semester model, along with
    filtering, ordering, and searching capabilities.

    Attributes:
        queryset: A queryset containing all Semester objects.
        serializer_class: The serializer class used for serializing and
            deserializing Semester objects.
        filter_backends: A list of filter backends used for filtering,
            ordering, and searching.
        filterset_fields: A dictionary specifying the fields that can be
            filtered, along with the lookup types allowed for each field.
        ordering_fields: A list of fields that can be used for ordering
            the results.
        ordering: The default ordering applied to the results.
        search_fields: A list of fields that can be searched using
            case-insensitive partial matches.
    """
    """Semester Model ViewSet."""

    queryset = models.Semester.objects.all()
    serializer_class = serializers.SemesterSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {"id": ["exact"], "name": ["exact", "icontains"]}
    ordering_fields = [
        "name",
    ]
    ordering = ["name"]
    search_fields = ["name"]


class ClassVS(viewsets.ModelViewSet):
    """
    A viewset for managing Class objects.

    This viewset provides CRUD operations for the Class model, along with
    filtering, ordering, and searching capabilities.

    Attributes:
        queryset (QuerySet): The queryset containing all Class objects.
        serializer_class (Serializer): The serializer class used for serializing
            and deserializing Class objects.
        filter_backends (list): A list of filter backends used for filtering,
            ordering, and searching.
        filterset_fields (dict): A dictionary specifying the fields that can be
            used for filtering. Supports exact and case-insensitive contains
            lookups for 'id' and 'name'.
        ordering_fields (list): A list of fields that can be used for ordering
            the results. Currently supports ordering by 'name'.
        ordering (list): The default ordering applied to the results. Defaults
            to ordering by 'name'.
        search_fields (list): A list of fields that can be used for searching.
            Currently supports searching by 'name'.
    """
    """Class Model ViewSet."""

    queryset = models.Class.objects.all()
    serializer_class = serializers.ClassSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = {"id": ["exact"], "name": ["exact", "icontains"]}
    ordering_fields = [
        "name",
    ]
    ordering = ["name"]
    search_fields = ["name"]


class ProfessorClassSectionVS(viewsets.ModelViewSet):
    """
    ProfessorClassSection Model ViewSet.

    This viewset provides CRUD operations for the ProfessorClassSection model
    and supports filtering, ordering, and searching on related fields.

    Attributes:
        queryset: The queryset containing all ProfessorClassSection objects.
        serializer_class: The serializer class used for serializing and
            deserializing ProfessorClassSection objects.
        filter_backends: A list of filter backends used for filtering, ordering,
            and searching.
        filterset_fields: A dictionary specifying the fields that can be
            filtered, including related fields with multiple lookup types:
            - "professor__id": Supports "exact" lookup.
            - "class_instance__name": Supports "exact" and "icontains" lookups.
            - "semester__name": Supports "exact" and "icontains" lookups.
        ordering_fields: A list of fields that can be used for ordering:
            - "professor__user__first_name"
            - "class_instance__name"
            - "semester__name"
        ordering: The default ordering applied to the queryset:
            - "semester__name"
            - "class_instance__name"
        search_fields: A list of fields that can be searched using a search query:
            - "class_instance__name"
            - "semester__name"
    """
    """ProfessorClassSection Model ViewSet."""

    queryset = models.ProfessorClassSection.objects.all()
    serializer_class = serializers.ProfessorClassSectionSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    # Filtering on related fields using dictionary syntax to
    # allow multiple lookup types.
    filterset_fields = {
        "professor__id": ["exact"],
        "class_instance__name": ["exact", "icontains"],
        "semester__name": ["exact", "icontains"],
    }
    ordering_fields = [
        "professor__user__first_name",
        "class_instance__name",
        "semester__name",
    ]
    ordering = ["semester__name", "class_instance__name"]
    # Allow searching by the names of the class instance and semester.
    search_fields = ["class_instance__name", "semester__name"]


class EnrollmentVS(viewsets.ModelViewSet):
    """
    A ViewSet for managing Enrollment objects.

    This ViewSet provides CRUD operations for the Enrollment model and supports
    filtering, ordering, and searching functionalities.

    Attributes:
        queryset (QuerySet): The default queryset for retrieving all Enrollment objects.
        serializer_class (Serializer): The serializer class used for Enrollment objects.
        permission_classes (list): A list of permission classes, requiring authentication.
        filter_backends (list): A list of filter backends for filtering, ordering, and searching.
        filterset_fields (dict): Fields available for filtering:
            - "student__id": Filter by exact student ID.
            - "class_instance__id": Filter by exact class instance ID.
            - "semester__id": Filter by exact semester ID.
        ordering_fields (list): Fields available for ordering:
            - "enrolled_date": Order by the enrollment date.
            - "semester__name": Order by the semester name.
        ordering (list): Default ordering applied to the queryset:
            - "enrolled_date": Ordered by enrollment date.
        search_fields (list): Fields available for searching:
            - "student__user__first_name": Search by the first name of the student.
            - "class_instance__name": Search by the name of the class instance.
            - "semester__name": Search by the name of the semester.
    """
    """Enrollment Model ViewSet."""

    queryset = models.Enrollment.objects.all()
    serializer_class = serializers.EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]

    # Allow filtering by student, class, and semester. Similar idea to other VS
    filterset_fields = {
        "student__id": ["exact"],
        "class_instance__id": ["exact"],
        "semester__id": ["exact"],
    }
    ordering_fields = ["enrolled_date", "semester__name"]
    ordering = ["enrolled_date"]
    search_fields = [
        "student__user__first_name",
        "class_instance__name",
        "semester__name",
    ]
