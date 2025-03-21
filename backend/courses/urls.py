"""
Courses URLs.
"""
from rest_framework.routers import DefaultRouter
#from rest_framework_nested.routers import NestedDefaultRouter
from courses.views import (ProfessorVS, ProfessorClassSectionVS, SemesterVS, ClassVS)
from django.urls import path, include

router = DefaultRouter()
router.register('classes', ClassVS, basename='class')
router.register('professors', ProfessorVS, basename='professor')
router.register('semesters', SemesterVS, basename='semester')
router.register('sectionclassprof', ProfessorClassSectionVS, basename='sectionclassprof')

urlpatterns = [
    path('', include(router.urls)),
]