"""Assignment Models Serializers."""

from rest_framework import serializers
from assignments import models
from courses import models as courses_models
from courses import serializers as courses_serializer


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for the Student model.

    This serializer converts Student model instances into JSON format and vice versa.
    It includes all fields of the Student model.
    Attributes:
        Meta (class): Contains metadata for the serializer, including the model to
        serialize and the fields to include.
    """

    class Meta:
        model = models.Student
        fields = "__all__"


class FlaggedStudentSerializer(serializers.ModelSerializer):
    """Serializer for the FlaggedStudent model.

    This serializer is used to handle the serialization and deserialization of
    FlaggedStudent objects. It includes all fields of the model and provides
    custom handling for the `student` and `student_id` fields.
    Attributes:
        student (StudentSerializer): A nested serializer for the related Student
            object. This field is read-only.
        student_id (serializers.PrimaryKeyRelatedField): A write-only field that
            allows setting the related Student object using its primary key. This
            field maps to the `student` field in the model.
    Meta:
        model (models.FlaggedStudent): The model associated with this serializer.
        fields (str): Specifies that all fields of the model should be included
            in the serialized output.
    """

    class Meta:
        model = models.FlaggedStudent
        fields = "__all__"

    student = StudentSerializer(read_only=True)

    student_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Student.objects.all(),
        source="student",
        write_only=True,
    )


class AssignmentSerializer(serializers.ModelSerializer):
    """AssignmentSerializer is a serializer for the Assignment model.

    It provides functionality
    for both read and write operations with nested relationships.
    Attributes:
        professor (ProfessorSerializer): A read-only nested serializer for the professor
            associated with the assignment.
        class_instance (ClassSerializer): A read-only nested serializer for the class
            instance associated with the assignment.
        professor_id (PrimaryKeyRelatedField): A write-only field that allows the client
            to specify the primary key (ID) of the professor when creating or updating
            an assignment.
        class_instance_id (PrimaryKeyRelatedField): A write-only field that allows the
            client to specify the primary key (ID) of the class instance when creating
            or updating an assignment.
    Meta:
        model (Assignment): The model that this serializer is based on.
        fields (str): Specifies that all fields of the model should be included in the
            serialized output.
    """

    class Meta:
        model = models.Assignment
        fields = "__all__"

    # For read operations: show nested details
    professor = courses_serializer.ProfessorSerializer(read_only=True)
    class_instance = courses_serializer.ClassSerializer(read_only=True)

    # For write operations: accept only IDs
    # since these are nested object its easier to simply declare them like so,
    # this will allow our client to specify the primary key (id) of the given
    # fields in their request to create new instances of ProffClassSection in
    # the databse
    professor_id = serializers.PrimaryKeyRelatedField(
        queryset=courses_models.Professor.objects.all(),
        source="professor",
        write_only=True,
    )
    class_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=courses_models.Class.objects.all(),
        source="class_instance",
        write_only=True,
    )


class SubmissionSerializer(serializers.ModelSerializer):
    """SubmissionSerializer is a serializer for the Submission model.

    It provides functionality
    for both read and write operations with nested relationships.
    Attributes:
        professor (ProfessorSerializer): A read-only nested serializer for the professor
            associated with the submission.
        student (StudentSerializer): A read-only nested serializer for the student
            associated with the submission.
        assignment (AssignmentSerializer): A read-only nested serializer for the assignment
            associated with the submission.
        professor_id (PrimaryKeyRelatedField): A write-only field to accept the ID of the
            professor associated with the submission.
        assignment_id (PrimaryKeyRelatedField): A write-only field to accept the ID of the
            assignment associated with the submission.
        student_id (PrimaryKeyRelatedField): A write-only field to accept the ID of the
            student associated with the submission.
    Meta:
        model (Submission): The model that this serializer is based on.
        fields (str): Specifies that all fields of the model should be included in the
            serialized output.
    """

    class Meta:
        model = models.Submission
        fields = "__all__"

    # For read operations: show nested details
    professor = courses_serializer.ProfessorSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    assignment = AssignmentSerializer(read_only=True)

    # For write operations: accept only IDs
    professor_id = serializers.PrimaryKeyRelatedField(
        queryset=courses_models.Professor.objects.all(),
        source="professor",
        write_only=True,
    )
    assignment_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Assignment.objects.all(),
        source="assignment",
        write_only=True,
    )
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Student.objects.all(),
        source="student",
        write_only=True,
    )


class FlaggedSubmissionSerializer(serializers.ModelSerializer):
    """FlaggedSubmissionSerializer is a serializer for the FlaggedSubmission
    model.

    This serializer handles both read and write operations:
    - For read operations, it provides nested details of related models (e.g., similarity_with and submission).
    - For write operations, it accepts only the IDs of related models (e.g., student_id and submission_id).
    Attributes:
        similarity_with (StudentSerializer): A read-only field that provides nested details of related students.
        submission (SubmissionSerializer): A read-only field that provides nested details of the related submission.
        student_id (PrimaryKeyRelatedField): A write-only field that accepts the ID of a related student.
        submission_id (PrimaryKeyRelatedField): A write-only field that accepts the ID of a related submission.
    Meta:
        model (FlaggedSubmission): The model associated with this serializer.
        fields (str): Specifies that all fields of the model should be included in the serialization.
    """

    class Meta:
        model = models.FlaggedSubmission
        fields = "__all__"

    # For read operations: show nested details
    similarity_with = StudentSerializer(read_only=True, many=True)
    submission = SubmissionSerializer(read_only=True)

    # For write operations: accept only IDs
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Student.objects.all(),
        source="student",
        write_only=True,
    )
    submission_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Submission.objects.all(),
        source="submission",
        write_only=True,
    )


class ConfirmedCheaterSerializer(serializers.ModelSerializer):
    """ConfirmedCheaterSerializer is a serializer for the ConfirmedCheater
    model.

    This serializer is used to handle the serialization and deserialization of
    ConfirmedCheater objects. It includes all fields from the model and provides
    additional functionality for handling related fields.
    Attributes:
        student (StudentSerializer): A nested serializer for the related Student
            object. This field is read-only.
        professor (ProfessorSerializer): A nested serializer for the related
            Professor object. This field is read-only.
        student_id (PrimaryKeyRelatedField): A write-only field for specifying the
            primary key of the related Student object. Maps to the `student` field.
        professor_id (PrimaryKeyRelatedField): A write-only field for specifying the
            primary key of the related Professor object. Maps to the `professor` field.
    Meta:
        model (ConfirmedCheater): The model that this serializer is based on.
        fields (str): Specifies that all fields in the model should be included in
            the serialization.
    """

    class Meta:
        model = models.ConfirmedCheater
        fields = "__all__"

    student = StudentSerializer(read_only=True)
    professor = courses_serializer.ProfessorSerializer(read_only=True)

    student_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Student.objects.all(),
        source="student",
        write_only=True,
    )
    professor_id = serializers.PrimaryKeyRelatedField(
        queryset=courses_models.Professor.objects.all(),
        source="professor",
        write_only=True,
    )
