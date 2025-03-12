"""
Assignments Views.
"""
from rest_framework import viewsets

from database.assignments import serializers, models
from database.courses import models as courses_models


class StudentVS(viewsets.ModelViewSet):
    """Student Model ViewSet."""
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer

class FlaggedStudentVS(viewsets.ModelViewSet):
    """Flagged Student Model ViewSet."""
    queryset = models.FlaggedStudent.objects.all()
    serializer_class = serializers.FlaggedStudentSerializer

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
        professor_instance = courses_models.Professor.objects.get(id=professor_id)
        #injecting here the professor instance validated data to save in our database with the
        #inf provided in the request
        serializer.save(professor=professor_instance)

class AssignmentVS(viewsets.ModelViewSet):
    """Assignment Model ViewSet."""
    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentSerializer

    def get_queryset(self):
        professor_id = self.kwargs.get('prof_pk')
        if professor_id:
            return self.queryset.filter(professor=professor_id)
        return self.queryset

    def perform_create(self, serializer):
        professor_id = self.kwargs.get('prof_pk')
        professor_instance = courses_models.Professor.objects.get(id=professor_id)
        serializer.save(professor=professor_instance)

class SubmissionVS(viewsets.ModelViewSet):
    """Submission Model ViewSet."""
    queryset = models.Submission.objects.all()
    serializer_class = serializers.SubmissionSerializer

    def get_queryset(self):
        professor_id = self.kwargs.get('prof_pk')
        if professor_id:
            return self.queryset.filter(professor=professor_id)
        return self.queryset

    def perform_create(self, serializer):
        professor_id = self.kwargs.get('prof_pk')
        professor_instance = courses_models.Professor.objects.get(id=professor_id)
        serializer.save(professor=professor_instance)

class FlaggedSubmissionVS(viewsets.ModelViewSet):
    """Flagged Submission Model ViewSet."""
    queryset = models.FlaggedSubmission.objects.all()
    serializer_class = serializers.FlaggedSubmissionSerializer

    def get_queryset(self):
        professor_id = self.kwargs.get('prof_pk')
        if professor_id:
            return self.queryset.filter(submission__professor=professor_id)
        return self.queryset

    def perform_create(self, serializer):
        professor_id = self.kwargs.get('prof_pk')
        # Extract the submission instance from validated data.
        submission = serializer.validated_data.get('submission')
        # Check if the submission belongs to the professor from the URL.
        if submission.professor.id != int(professor_id):
            raise serializers.ValidationError("Submission does not belong to the specified professor.")
        serializer.save()

class ConfirmedCheaterVS(viewsets.ModelViewSet):
    """Confirmed Cheater Model ViewSet."""
    queryset = models.ConfirmedCheater.objects.all()
    serializer_class = serializers.ConfirmedCheaterSerializer

    def get_queryset(self):
        professor_id = self.kwargs.get('prof_pk')
        if professor_id:
            return self.queryset.filter(professor=professor_id)
        return self.queryset

    def perform_create(self, serializer):
        professor_id = self.kwargs.get('prof_pk')
        professor_instance = courses_models.Professor.objects.get(id=professor_id)
        serializer.save(professor=professor_instance)






