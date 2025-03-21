"""
Courses Views with Enhanced Filtering, Ordering, and Search Capabilities.
"""

from courses import serializers
from courses import models
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters import rest_framework as filters


class ProfessorVS(viewsets.ModelViewSet):
    """Professor Model ViewSet."""

    queryset = models.Professor.objects.all()
    serializer_class = serializers.ProfessorSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = {"id": ["exact"], "user__first_name": ["exact", "icontains"]}
    ordering_fields = ["user__first_name"]
    ordering = ["user__first_name"]
    search_fields = ["user__first_name"]


class SemesterVS(viewsets.ModelViewSet):
    """Semester Model ViewSet."""

    queryset = models.Semester.objects.all()
    serializer_class = serializers.SemesterSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter, SearchFilter]
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
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter, SearchFilter]
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
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter, SearchFilter]
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
        # 'prof_pk' comes from the nested router lookup
        # this will allow example GET /professor/4/semprofclass/
        # types of situations to be possible
        professor_id = self.kwargs.get("prof_pk")
        # if something was passed then return the specific info for that professor
        if professor_id:
            return self.queryset.filter(professor=professor_id)
        # else return the whole list
        return self.queryset

    def perform_create(self, serializer):
        professor_id = self.kwargs.get("prof_pk")
        professor_instance = models.Professor.objects.get(id=professor_id)
        # injecting here the professor instance validated data to save in our database with the
        # inf provided in the request
        serializer.save(professor=professor_instance)
