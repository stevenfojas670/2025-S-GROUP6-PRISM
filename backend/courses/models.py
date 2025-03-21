"""
Courses Database Models.
"""
from django.db import models
from users import models as user_model
from django.conf import settings

class Professor(models.Model):
    """Professor Model."""
    user = models.OneToOneField(user_model.User, on_delete=models.CASCADE, related_name="user_professor")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Class(models.Model):
    """Class Model."""
    name = models.CharField(max_length=50, unique=True)

    # Explicitly reference the Professor model from the users app
    professors = models.ManyToManyField(
        "courses.Professor",
        #the join table will happen at the ProfessorClassSection instead of being created automatic bewteen prof and class
        through="ProfessorClassSection",
    )

    def __str__(self):
        return self.name

class Semester(models.Model):
    """Semesters Model."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ProfessorClassSection(models.Model):
    """Mapping Professors to Class Sections."""
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE, related_name="profclassect")
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    section_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.professor} - {self.class_instance} - {self.semester} (Section {self.section_number})"
