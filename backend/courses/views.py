"""
Courses Views with Enhanced Filtering, Ordering, and Search Capabilities.
"""

from courses import serializers
from courses import models
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404


class BaseModelViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]


class ProfessorVS(BaseModelViewSet):
    """Professor Model ViewSet."""

    queryset = models.Professor.objects.all()
    serializer_class = serializers.ProfessorSerializer
    filterset_fields = {"id": ["exact"], "user__first_name": ["exact", "icontains"]}
    ordering_fields = ["user__first_name"]
    ordering = ["user__first_name"]
    search_fields = ["user__first_name"]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return models.Professor.objects.all()
        return models.Professor.objects.filter(user=user)


class SemesterVS(BaseModelViewSet):
    """Semester Model ViewSet."""

    queryset = models.Semester.objects.all()
    serializer_class = serializers.SemesterSerializer
    filterset_fields = {"id": ["exact"], "name": ["exact", "icontains"]}
    ordering_fields = [
        "name",
    ]
    ordering = ["name"]
    search_fields = ["name"]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return models.Semester.objects.filter()
        return models.Semester.objects.filter(
            professorclasssection__professor__user=user
        )


class ClassVS(BaseModelViewSet):
    """Class Model ViewSet."""

    queryset = models.Class.objects.all()
    serializer_class = serializers.ClassSerializer
    filterset_fields = {"id": ["exact"], "name": ["exact", "icontains"]}
    ordering_fields = [
        "name",
    ]
    ordering = ["name"]
    search_fields = ["name"]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return models.Class.objects.all()
        return models.Class.objects.filter(professors__user=user)


class ProfessorClassSectionVS(BaseModelViewSet):
    """ProfessorClassSection Model ViewSet."""

    queryset = models.ProfessorClassSection.objects.all()
    serializer_class = serializers.ProfessorClassSectionSerializer
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

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return models.ProfessorClassSection.objects.all()
        return models.ProfessorClassSection.objects.filter(professor__user=user)

    def perform_create(self, serializer):
        professor_id = self.kwargs.get("prof_pk")
        professor_instance = get_object_or_404(models.Professor, id=professor_id)
        # injecting here the professor instance validated data to save in our database with the
        # inf provided in the request
        serializer.save(professor=professor_instance)
