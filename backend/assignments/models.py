from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Student(models.Model):
    """Represents a student entity with personal and academic information.

    Attributes:
        email (EmailField): The unique email address of the student.
        codeGrade_id (IntegerField): A unique identifier for the student in CodeGrade.
        username (CharField): The optional username of the student, which may be provided by CodeGrade.
        first_name (CharField): The first name of the student.
        last_name (CharField): The last name of the student.
    Methods:
        __str__(): Returns a string representation of the student in the format
                "FirstName LastName (Email)".
    """

    email = models.EmailField(max_length=100, unique=True)
    codeGrade_id = models.IntegerField(
        unique=True
    )  # This is for the code_gradeID field in codegrade
    username = models.CharField(
        max_length=50, blank=True, null=True
    )  # Optional; maybe CodeGrade has this info?
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        """Returns a string representation of the object, including the first
        name, last name, and email in the format: "FirstName LastName
        (Email)"."""
        return f"{self.first_name} {self.last_name} ({self.email})"


class Assignment(models.Model):
    """Represents an assignment for a specific class instance, linked to a
    professor.

    Attributes:
        class_instance (ForeignKey): A foreign key linking the assignment to a specific class instance.
        professor (ForeignKey): A foreign key linking the assignment to a professor.
        assignment_number (IntegerField): The unique number of the assignment within the class instance.
        title (CharField): The title of the assignment, with a maximum length of 100 characters.
        due_date (DateField): The due date of the assignment.
    Meta:
        unique_together: Ensures that the combination of `class_instance` and `assignment_number` is unique.
    Methods:
        __str__(): Returns a string representation of the assignment in the format
                   "Assignment {assignment_number}: {title}".
    """

    class_instance = models.ForeignKey("courses.Class", on_delete=models.CASCADE)
    professor = models.ForeignKey(
        "courses.Professor", on_delete=models.CASCADE
    )  # Link to professor
    assignment_number = models.IntegerField()
    title = models.CharField(max_length=100)
    due_date = models.DateField()

    class Meta:
        unique_together = (
            "class_instance",
            "assignment_number",
        )  # Unique per class

    def __str__(self):
        """Returns a string representation of the Assignment object.

        The string includes the assignment number and title in the format:
        "Assignment <assignment_number>: <title>".

        Returns:
            str: A formatted string representing the assignment.
        """
        return f"Assignment {self.assignment_number}: {self.title}"


class Submission(models.Model):
    """Represents a submission made by a student for a specific assignment.

    Attributes:
        student (Student): The student who made the submission. Linked via a foreign key.
        assignment (Assignment): The assignment for which the submission was made. Linked via a foreign key.
        grade (int): The grade assigned to the submission. Must be between 0 and 100.
        created_at (date): The date when the submission was created. Automatically set on creation.
        flagged (bool): Indicates whether the submission has been flagged for review. Defaults to False.
        professor (Professor): The professor associated with the submission. Linked via a foreign key.
    Methods:
        __str__(): Returns a string representation of the submission, including the student and assignment details.
    """

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateField(auto_now_add=True)
    flagged = models.BooleanField(default=False)
    professor = models.ForeignKey(
        "courses.Professor", on_delete=models.CASCADE
    )  # Link to professor

    def __str__(self):
        """Returns a string representation of the submission, including the
        student's name and the associated assignment."""
        return f"Submission by {self.student} for {self.assignment}"


class FlaggedSubmission(models.Model):
    """Represents a flagged submission in the system, typically used to
    indicate potential plagiarism or similarity issues between student
    submissions.

    Attributes:
        submission (ForeignKey): A reference to the related `Submission` object.
            If the related submission is deleted, this flagged submission will
            also be deleted.
        file_name (CharField): The name of the file associated with the flagged
            submission. Maximum length is 50 characters.
        percentage (IntegerField): The percentage similarity of the flagged
            submission. Must be between 20 and 100, inclusive.
        similarity_with (ManyToManyField): A many-to-many relationship with
            `Student` objects, representing other students whose submissions
            have similarities with this flagged submission.
    Methods:
        __str__(): Returns a string representation of the flagged submission,
            including the file name and similarity percentage.
    """

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50)
    percentage = models.IntegerField(
        validators=[MinValueValidator(20), MaxValueValidator(100)]
    )
    similarity_with = models.ManyToManyField(
        Student, related_name="similar_submissions"
    )  # Supports multiple similarities

    def __str__(self):
        """Returns a string representation of the flagged submission, including
        the file name and the percentage value.

        Returns:
            str: A formatted string in the format "Flagged Submission: <file_name> (<percentage>%)".
        """
        return f"Flagged Submission: {self.file_name} ({self.percentage}%)"


class FlaggedStudent(models.Model):
    """Represents a student who has been flagged for exceeding a certain
    threshold.

    Attributes:
        student (ForeignKey): A reference to the flagged student, linked to the Student model.
        professor (ForeignKey): A reference to the professor who flagged the student, linked to the Professor model in the courses app.
        times_over_threshold (IntegerField): The number of times the student has exceeded the threshold. Defaults to 0.
    Methods:
        __str__(): Returns a string representation of the flagged student and the number of times they have been flagged.
    """

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE)
    times_over_threshold = models.IntegerField(default=0)

    def __str__(self):
        """Returns a string representation of the object, indicating the
        flagged student and the number of times they have exceeded the
        threshold.

        Returns:
            str: A formatted string containing the student's name and the count of times
            they were flagged over the threshold.
        """
        return (
            f"Flagged Student: {self.student} "
            f"flagged {self.times_over_threshold} times"
        )


class ConfirmedCheater(models.Model):
    """Model representing a confirmed cheater in the system.

    Attributes:
        student (ForeignKey): A foreign key linking to the Student model, representing the student confirmed as a cheater.
        professor (ForeignKey): A foreign key linking to the Professor model in the "courses" app, representing the professor who confirmed the cheating.
        confirmed_date (DateField): The date when the cheating was confirmed. Automatically set to the current date when the record is created.
        threshold_used (IntegerField): The threshold percentage used to confirm the cheating. Defaults to 40.
    Methods:
        __str__(): Returns a string representation of the confirmed cheater, including the student's name, confirmation date, and threshold used.
    """

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    professor = models.ForeignKey("courses.Professor", on_delete=models.CASCADE)
    confirmed_date = models.DateField(auto_now_add=True)
    threshold_used = models.IntegerField(
        default=40
    )  # Tracks threshold used at confirmation

    def __str__(self):
        """Returns a string representation of the object, providing details
        about a confirmed cheater, including the student's name, the date of
        confirmation, and the threshold percentage used."""
        return (
            f"Confirmed Cheater: {self.student} "
            f"on {self.confirmed_date} "
            f"(Threshold: {self.threshold_used}%)"
        )
