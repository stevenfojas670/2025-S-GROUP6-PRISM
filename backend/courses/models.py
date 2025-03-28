"""Courses Database Models."""

from django.db import models
from users import models as user_model
from assignments.models import Student


class Professor(models.Model):
    """
    Represents a professor in the system.

    Attributes:
        user (OneToOneField): A one-to-one relationship with the User model,
            representing the user account associated with the professor.
            Deleting the professor will also delete the associated user account.

    Methods:
        __str__(): Returns the full name of the professor as a string
            (first name followed by last name).
    """
    """Professor Model."""

    user = models.OneToOneField(
        user_model.User,
        on_delete=models.CASCADE,
        related_name="user_professor",
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Class(models.Model):
    """
    Represents a class or course in the system.

    Attributes:
        name (str): The name of the class. Must be unique and have a maximum length of 50 characters.
        professors (ManyToManyField): A many-to-many relationship with the Professor model,
            explicitly defined through the ProfessorClassSection model.

    Methods:
        __str__(): Returns the string representation of the class, which is its name.
    """
    """Class Model."""

    name = models.CharField(max_length=50, unique=True)

    # Explicitly reference the Professor model from the users app
    professors = models.ManyToManyField(
        "courses.Professor",
        # the join table will happen at the ProfessorClassSection instead of
        # being created automatic bewteen prof and class
        through="ProfessorClassSection",
    )

    def __str__(self):
        return self.name


class Semester(models.Model):
    """
    Represents a semester in the system.

    Attributes:
        name (str): The name of the semester. Must be unique and have a maximum length of 50 characters.

    Methods:
        __str__(): Returns the string representation of the semester, which is its name.
    """
    """Semesters Model."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ProfessorClassSection(models.Model):
    """
    Represents a mapping between a professor, a class instance, and a semester,
    with an optional section number.

    Attributes:
        professor (ForeignKey): A foreign key to the Professor model, representing
            the professor associated with the class section.
        class_instance (ForeignKey): A foreign key to the Class model, representing
            the class instance being taught.
        semester (ForeignKey): A foreign key to the Semester model, representing
            the semester in which the class section is offered.
        section_number (IntegerField): An optional integer field representing the
            section number of the class.

    Methods:
        __str__(): Returns a string representation of the ProfessorClassSection
            instance in the format:
            "<professor> - <class_instance> - <semester> (Section <section_number>)".
    """
    """Mapping Professors to Class Sections."""

    professor = models.ForeignKey(
        "courses.Professor",
        on_delete=models.CASCADE,
        related_name="profclassect",
    )
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    section_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return (
            f"{self.professor} - {self.class_instance} - {self.semester} "
            f"(Section {self.section_number})"
        )


class Enrollment(models.Model):
    """Tracks student enrollment status in classes.

    'student' will represent an entire student row from that specific
    table. Thats how its set up with the foreign key. It means we can do
    this: print(enrollment.student) or this too
    print(enrollment.student.email)
    """

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)
    dropped = models.BooleanField(default=False)  # Flag for if they dropped
    dropped_date = models.DateField(
        blank=True, null=True
    )  # Timestamp of when they dropped

    # this should prevent duplicate enrollments
    class Meta:
        unique_together = ("student", "class_instance", "semester")

    def __str__(self):
        return f"{self.student} enrolled in {self.class_instance} " f"({self.semester})"
