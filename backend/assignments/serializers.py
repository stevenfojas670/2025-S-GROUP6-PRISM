"""
Assignment Models Serializers.
"""

from rest_framework import serializers
from assignments import models
from courses import models as courses_models
from courses import serializers as courses_serializer


class StudentSerializer(serializers.ModelSerializer):
    """Student Models Serializers."""

    class Meta:
        model = models.Student
        fields = "__all__"


class FlaggedStudentSerializer(serializers.ModelSerializer):
    """Flagged Student Models Serializers."""

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
    """Assignment Models Serializers."""

    class Meta:
        model = models.Assignment
        fields = "__all__"

    # For read operations: show nested details
    professor = courses_serializer.ProfessorSerializer(read_only=True)
    class_instance = courses_serializer.ClassSerializer(read_only=True)

    # For write operations: accept only IDs
    # since these are nested object its easier to simply declare them like so,
    # this will allow our client to specify the primary key (id) of the given fields
    # in their request to create new instances of ProffClassSection in the databse
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
    """Submission Models Serializers."""

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
    """Flagged Submission Models Serializers."""

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
    """Confirmed Cheater Models Serializers."""

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
