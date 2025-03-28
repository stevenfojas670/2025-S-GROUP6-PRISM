"""
Courses Views with Enhanced Filtering, Ordering, and Search Capabilities.
"""

from courses import serializers
from courses import models
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import rest_framework as filters


class ProfessorVS(viewsets.ModelViewSet):
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
    """ProfessorClassSection Model ViewSet."""

    queryset = models.ProfessorClassSection.objects.all()
    serializer_class = serializers.ProfessorClassSectionSerializer
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    # Filtering on related fields using dictionary syntax to allow multiple lookup types.
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
