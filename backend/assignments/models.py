from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Student(models.Model):
    """Students Model."""
    email = models.EmailField(max_length=100, unique=True)
    codeGrade_id = models.IntegerField(unique=True)  # This is for the code_gradeID field in codegrade
    username = models.CharField(max_length=50, blank=True, null=True)  # Optional; maybe CodeGrade has this info?
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Assignment(models.Model):
    """Assignment Model."""
    class_instance = models.ForeignKey("courses.Class", on_delete=models.CASCADE)
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE)  # Link to professor
    assignment_number = models.IntegerField()
    title = models.CharField(max_length=100)
    due_date = models.DateField()

    class Meta:
        unique_together = ('class_instance', 'assignment_number')  # Unique per class

    def __str__(self):
        return f"Assignment {self.assignment_number}: {self.title}"

class Submission(models.Model):
    """Submissions Model."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateField(auto_now_add=True)
    flagged = models.BooleanField(default=False)
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE)  # Link to professor

    def __str__(self):
        return f"Submission by {self.student} for {self.assignment}"

class FlaggedSubmission(models.Model):
    """Flagged Submissions Model."""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50)
    percentage = models.IntegerField(validators=[MinValueValidator(20), MaxValueValidator(100)])
    similarity_with = models.ManyToManyField(Student, related_name="similar_submissions")  # Supports multiple similarities

    def __str__(self):
        return f"Flagged Submission: {self.file_name} ({self.percentage}%)"

class FlaggedStudent(models.Model):
    """Flagged Students Model."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE)
    times_over_threshold = models.IntegerField(default=0)

    def __str__(self):
        return f"Flagged Student: {self.student} flagged {self.times_over_threshold} times"

class ConfirmedCheater(models.Model):
    """Confirmed Cheaters Model."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE)
    confirmed_date = models.DateField(auto_now_add=True)
    threshold_used = models.IntegerField(default=40)  # Tracks threshold used at confirmation

    def __str__(self):
        return f"Confirmed Cheater: {self.student} on {self.confirmed_date} (Threshold: {self.threshold_used}%)"
