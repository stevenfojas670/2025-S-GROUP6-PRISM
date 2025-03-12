"""
Courses Views.
"""
from database.courses import serializers
from database.courses import models
from rest_framework import viewsets

class ProfessorVS(viewsets.ModelViewSet):
    """Professor Model ViewSet."""
    queryset = models.Professor.objects.all()
    serializer_class = serializers.ProfessorSerializer

class SemesterVS(viewsets.ModelViewSet):
    """Semester Model ViewSet."""
    queryset = models.Semester.objects.all()
    serializer_class = serializers.SemesterSerializer

class ClassVS(viewsets.ModelViewSet):
    """Class Model ViewSet."""
    queryset = models.Class.objects.all()
    serializer_class = serializers.ClassSerializer

class ProfessorClassSectionVS(viewsets.ModelViewSet):
    """ProfessorClassSection Model ViewSet."""
    queryset = models.ProfessorClassSection.objects.all()
    serializer_class = serializers.ProfessorClassSectionSerializer

    def get_queryset(self):
        # 'prof_pk' comes from the nested router lookup
        #this will allow example GET /professor/4/semprofclass/
        #types of situations to be possible
        professor_id = self.kwargs.get('prof_pk')
        #if something was passed then return the specific info for that professor
        if professor_id:
            return self.queryset.filter(professor=professor_id)
        #else return the whole list
        return self.queryset

    def perform_create(self, serializer):
        professor_id = self.kwargs.get('prof_pk')
        professor_instance = models.Professor.objects.get(id=professor_id)
        #injecting here the professor instance validated data to save in our database with the
        #inf provided in the request
        serializer.save(professor=professor_instance)
