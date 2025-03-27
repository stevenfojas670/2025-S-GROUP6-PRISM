
"""
Courses Database Models.
"""
from django.db import models
from users import models as user_model
from django.conf import settings
from assignments.models import Student

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

class Enrollment(models.Model):
    """Tracks student enrollment status in classes.
    'student' will represent an entire student row from that specific table. Thats how its set up with the foreign key.
    it means we can do this: print(enrollment.student) or this too print(enrollment.student.email)"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)
    dropped = models.BooleanField(default=False)  # Flag for if they dropped
    dropped_date = models.DateField(blank=True, null=True)  # Timestamp of when they dropped

    # this should prevent duplicate enrollments
    class Meta:
        unique_together = ('student', 'class_instance', 'semester')  

    def __str__(self):
        return f"{self.student} enrolled in {self.class_instance} ({self.semester})"