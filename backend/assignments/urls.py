"""
Assignments URLs.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from assignments.views import (
    AssignmentVS,
    SubmissionVS,
    FlaggedSubmissionVS,
    FlaggedStudentVS,
    ConfirmedCheaterVS,
    StudentVS
)
from courses.views import ProfessorVS

# Base router for professors.
# This will generate the URLs like this: /professor/{prof_pk}/ so we can filfter using professor wich is the main guy here
professor_router = DefaultRouter()
professor_router.register('professor', ProfessorVS, basename='professor')

# nested router: nest assignment endpoints under the professor.
# using lookup 'prof' means that the nested router will pass a parameter 'prof_pk' to the viewsets.
assignment_nested_router = NestedDefaultRouter(professor_router, r'professor', lookup='prof')
# Now i will register the assignment app endpoints with the nested router that i set above
#cleeeeeean
assignment_nested_router.register('assignments', AssignmentVS, basename='professor-assignments')
assignment_nested_router.register('submissions', SubmissionVS, basename='professor-submissions')
assignment_nested_router.register('flagged-submission', FlaggedSubmissionVS, basename='professor-flagged-submission')
assignment_nested_router.register('flagged-student', FlaggedStudentVS, basename='professor-flagged-student')
assignment_nested_router.register('confirmed-cheater', ConfirmedCheaterVS, basename='professor-confirmed-cheater')
assignment_nested_router.register('student', StudentVS, basename='professor-student')

urlpatterns = [
    path('', include(professor_router.urls)),
    path('', include(assignment_nested_router.urls)),
]