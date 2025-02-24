"""
Courses URLs.
"""
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from courses.views import (ProfessorVS, ProfessorClassSectionVS, SemesterVS, ClassVS)
from django.urls import path, include

class_router = DefaultRouter()
class_router.register('class', ClassVS, basename='class-urls')

professor_router = DefaultRouter()
professor_router.register('professor', ProfessorVS, basename='professor-urls')

#/professor/2/semprofclass/ type of URL, where 2 is the professorID
prof_nested_router = NestedDefaultRouter(professor_router, r'professor', lookup='prof')
prof_nested_router.register(r'semprofclass', ProfessorClassSectionVS, basename='professor-semprofclass')

semester_router = DefaultRouter()
semester_router.register('semester', SemesterVS, basename='semester-urls')

urlpatterns = [
    path('', include(class_router.urls)),
    path('', include(professor_router.urls)),
    path('', include(prof_nested_router.urls)),
    path('', include(semester_router.urls)),
]