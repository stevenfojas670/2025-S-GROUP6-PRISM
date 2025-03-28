"""Courses Models Serializers."""

from rest_framework import serializers
from courses import models
from users import serializers as user_serializer


class ProfessorSerializer(serializers.ModelSerializer):
    """Serializer for the Professor model.

    This serializer is used to convert Professor model instances into JSON format
    and vice versa. It includes all fields of the Professor model and uses the
    `UserSerializer` to represent the related `user` field in a read-only manner.

    Attributes:
        user (UserSerializer): A nested serializer for the related user object,
            set to read-only.

    Meta:
        model (Professor): The model associated with this serializer.
        fields (str): Specifies that all fields of the model should be included
            in the serialized output.
    """

    """Professor Model Serializer."""

    user = user_serializer.UserSerializer(read_only=True)

    class Meta:
        model = models.Professor
        fields = "__all__"


# create() and update() methods are already implemented here by default
class ClassSerializer(serializers.ModelSerializer):
    """Serializer for the Class model.

    This serializer is used to convert instances of the Class model
    to and from JSON format. It includes the following fields:
    - name: The name of the class.

    Attributes:
        Meta (class): Contains metadata for the serializer, including the
        associated model and the fields to be serialized.
    """

    """Class Model Serializer."""

    class Meta:
        model = models.Class
        fields = ["name"]


class SemesterSerializer(serializers.ModelSerializer):
    """Serializer for the Semester model.

    This serializer is used to convert Semester model instances into JSON format
    and validate incoming data for creating or updating Semester instances.

    Attributes:
        Meta (class): Contains metadata for the serializer, including the model
            it is based on and the fields to include in the serialization.
    """

    """Semester Model Serializer."""

    class Meta:
        model = models.Semester
        fields = ["name"]


class ProfessorClassSectionSerializer(serializers.ModelSerializer):
    """ProfessorClassSectionSerializer is a ModelSerializer for the
    ProfessorClassSection model.

    This serializer handles both read and write operations for the ProfessorClassSection model:
    - For read operations, it provides nested details for the `semester` and `class_instance` fields.
    - For write operations, it accepts only primary key IDs for the `semester`, `class_instance`, and `professor` fields.

    Attributes:
        semester (SemesterSerializer): A nested serializer for the Semester model (read-only).
        class_instance (ClassSerializer): A nested serializer for the Class model (read-only).
        semester_id (PrimaryKeyRelatedField): A field to accept the primary key of the Semester model (write-only).
        class_instance_id (PrimaryKeyRelatedField): A field to accept the primary key of the Class model (write-only).
        professor_id (PrimaryKeyRelatedField): A field to accept the primary key of the Professor model (write-only).

    Meta:
        model (ProfessorClassSection): The model associated with this serializer.
        fields (list): The fields included in the serializer:
            - "section_number": The section number of the class.
            - "semester": Nested details of the semester (read-only).
            - "semester_id": Primary key of the semester (write-only).
            - "class_instance": Nested details of the class instance (read-only).
            - "class_instance_id": Primary key of the class instance (write-only).
            - "professor_id": Primary key of the professor (write-only).
    """

    """ProfessorClassSection Model Serializer."""

    # For read operations: show nested details
    semester = SemesterSerializer(read_only=True)
    class_instance = ClassSerializer(read_only=True)

    # For write operations: accept only IDs
    # since these are nested object its easier to simply declare them like so,
    # this will allow our client to specify the primary key (id) of the given
    # fields in their request to create new instances of ProffClassSection in
    # the databse
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Semester.objects.all(),
        source="semester",
        write_only=True,
    )
    class_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Class.objects.all(),
        source="class_instance",
        write_only=True,
    )
    professor_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Professor.objects.all(),
        source="professor",
        write_only=True,
    )

    class Meta:
        model = models.ProfessorClassSection
        fields = [
            "section_number",
            "semester",
            "semester_id",
            "class_instance",
            "class_instance_id",
            "professor_id",
        ]


# Serializer stuff lets us send data to frontend with API responses.
# Also validates incoming JSON data and helps by converting to an enrollment
# object when creating/updating records.
# Similar structure to PCSSerializer
class EnrollmentSerializer(serializers.ModelSerializer):
    """
    EnrollmentSerializer is a Django REST Framework (DRF) serializer for the Enrollment model.
    It is designed to handle both read and write operations efficiently by customizing the
    representation of related fields.

    Attributes:
        student (StringRelatedField): A read-only field that provides a string representation
            of the related Student object for read operations.
        class_instance (StringRelatedField): A read-only field that provides a string
            representation of the related Class object for read operations.
        semester (StringRelatedField): A read-only field that provides a string representation
            of the related Semester object for read operations.
        student_id (PrimaryKeyRelatedField): A write-only field that accepts the primary key
            (ID) of a Student object and maps it to the `student` field in the Enrollment model.
        class_instance_id (PrimaryKeyRelatedField): A write-only field that accepts the primary
            key (ID) of a Class object and maps it to the `class_instance` field in the Enrollment model.
        semester_id (PrimaryKeyRelatedField): A write-only field that accepts the primary key
            (ID) of a Semester object and maps it to the `semester` field in the Enrollment model.

    Meta:
        model (Enrollment): Specifies the Enrollment model as the target model for this serializer.
        fields (list): Defines the fields to be included in the serialized representation.
            These include:
            - "id": The unique identifier of the enrollment.
            - "student": The string representation of the related Student object.
            - "student_id": The primary key of the related Student object (write-only).
            - "class_instance": The string representation of the related Class object.
            - "class_instance_id": The primary key of the related Class object (write-only).
            - "semester": The string representation of the related Semester object.
            - "semester_id": The primary key of the related Semester object (write-only).
            - "enrolled_date": The date the student was enrolled.
            - "dropped": A boolean indicating whether the student has dropped the class.
            - "dropped_date": The date the student dropped the class (if applicable).

    This serializer is optimized for frontend use by providing detailed string representations
    of related objects for read operations, while allowing efficient write operations using
    primary keys. It also reduces database queries, improving performance.
    """
    """Enrollment Model Serializer."""

    # For read operations, show full student/class/semester details. without
    # this, the data thats returned for these would be just ids.
    # This makes the data quickly readable for frontend.
    # This works bc frontend probably just needs these names, and not the
    # full detailes about each object.
    # It reduces db queries => improved performance
    student = serializers.StringRelatedField(read_only=True)
    class_instance = serializers.StringRelatedField(read_only=True)
    semester = serializers.StringRelatedField(read_only=True)

    # Just accepting ids for writes. Same reasoning as PCSSerializer. i.e. he
    # client can just specify a student_id, instead
    # of an entire student object. It also maps the student_id to the actual
    # 'student' field in the enrollment (source='student')
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Student.objects.all(),
        source="student",
        write_only=True,
    )
    class_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Class.objects.all(),
        source="class_instance",
        write_only=True,
    )
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Semester.objects.all(),
        source="semester",
        write_only=True,
    )

    # This gives frontend requests full details of student, class, and semeste
    # (rather than just ids) I think the frontend can now just specify a
    # student_id { "student_id": 1 }, instead of nesting a full student because
    # of this.
    class Meta:
        model = models.Enrollment
        fields = [
            "id",
            "student",
            "student_id",
            "class_instance",
            "class_instance_id",
            "semester",
            "semester_id",
            "enrolled_date",
            "dropped",
            "dropped_date",
        ]
