from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Student(models.Model):
    """Students Model."""
    email = models.EmailField(max_length=100, unique=True)
    student_id = models.IntegerField(unique=True)  # This is for the code_gradeID field in codegrade
    username = models.CharField(max_length=50, blank=True, null=True)  # Optional
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

class Assignment(models.Model):
    """Assignment Model."""
    class_instance = models.ForeignKey("courses.Class", on_delete=models.CASCADE)
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE)  # Link to professor
    assignment_number = models.IntegerField()
    title = models.CharField(max_length=100)
    due_date = models.DateField()

    class Meta:
        unique_together = ('class_instance', 'assignment_number')  # Unique per class

class Submission(models.Model):
    """Submissions Model."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateField(auto_now_add=True)
    flagged = models.BooleanField(default=False)
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE)  # Link to professor

class FlaggedSubmission(models.Model):
    """Flagged Submissions Model."""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50)
    percentage = models.IntegerField(validators=[MinValueValidator(20), MaxValueValidator(100)])
    similarity_with = models.ManyToManyField(Student, related_name="similar_submissions")  # Supports multiple similarities

class FlaggedStudent(models.Model):
    """Flagged Students Model."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    times_over_threshold = models.IntegerField(default=0)

class ConfirmedCheater(models.Model):
    """Confirmed Cheaters Model."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    confirmed_date = models.DateField(auto_now_add=True)
    threshold_used = models.IntegerField(default=40)  # Tracks threshold used at confirmation
