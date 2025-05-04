"""Serializers for the Assignments app."""

from rest_framework import serializers
from courses import serializers as courseSerializers

from .models import (
    Assignments,
    Submissions,
    BaseFiles,
    BulkSubmissions,
    Constraints,
    PolicyViolations,
    RequiredSubmissionFiles,
)


class AssignmentsSerializer(serializers.ModelSerializer):
    """Serializer for the Assignments model."""

    class Meta:
        """Meta options for the AssignmentsSerializer.

        Attributes:
            model: The model class that this serializer serializes.
            fields: All model fields are included.
        """

        model = Assignments
        fields = "__all__"


class SubmissionsSerializer(serializers.ModelSerializer):
    """Serializer for the Submissions model."""

    student = courseSerializers.StudentsSerializer()
    assignment = AssignmentsSerializer()

    class Meta:
        """Meta options for the SubmissionsSerializer.

        Attributes:
            model: The model class that this serializer serializes.
            fields: All model fields are included.
        """

        model = Submissions
        fields = "__all__"


class BaseFilesSerializer(serializers.ModelSerializer):
    """Serializer for the BaseFiles model."""

    assignment = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """Meta options for the BaseFilesSerializer.

        Attributes:
            model: The model class that this serializer serializes.
            fields: All model fields are included.
        """

        model = BaseFiles
        fields = "__all__"


class BulkSubmissionsSerializer(serializers.ModelSerializer):
    """Serializer for the BulkSubmissions model."""

    class Meta:
        """Meta options for the BulkSubmissionsSerializer.

        Attributes:
            model: The model class that this serializer serializes.
            fields: All model fields are included.
        """

        model = BulkSubmissions
        fields = "__all__"


class ConstraintsSerializer(serializers.ModelSerializer):
    """Serializer for the Constraints model."""

    assignment = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """Meta options for the ConstraintsSerializer.

        Attributes:
            model: The model class that this serializer serializes.
            fields: All model fields are included.
        """

        model = Constraints
        fields = "__all__"


class PolicyViolationsSerializer(serializers.ModelSerializer):
    """Serializer for the PolicyViolations model."""

    class Meta:
        """Meta options for the PolicyViolationsSerializer.

        Attributes:
            model: The model class that this serializer serializes.
            fields: All model fields are included.
        """

        model = PolicyViolations
        fields = "__all__"


class RequiredSubmissionFilesSerializer(serializers.ModelSerializer):
    """Serializer for the RequiredSubmissionFiles model."""

    assignment = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        """Meta options for the RequiredSubmissionFilesSerializer.

        Attributes:
            model: The model class that this serializer serializes.
            fields: All model fields are included.
        """

        model = RequiredSubmissionFiles
        fields = "__all__"


class AssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Assignments with nested related data."""

    base_files = BaseFilesSerializer(many=True, required=False)
    required_files = RequiredSubmissionFilesSerializer(
        many=True, required=True, min_length=1
    )
    constraints = ConstraintsSerializer(many=True, required=False)

    class Meta:
        """Meta options for AssignmentCreateSerializer.

        Attributes:
            model: The Assignments model class.
            fields: All model fields including nested related data.
        """

        model = Assignments
        fields = [
            "id",
            "course_catalog",
            "semester",
            "assignment_number",
            "title",
            "due_date",
            "lock_date",
            "pdf_filepath",
            "has_base_code",
            "moss_report_directory_path",
            "bulk_ai_directory_path",
            "language",
            "has_policy",
            "base_files",
            "required_files",
            "constraints",
        ]

    def create(self, validated_data):
        """Create a new assignment with optional base files, required files, and constraints.

        Args:
            validated_data (dict): Validated data for the assignment and nested objects.

        Returns:
            Assignments: The created assignment instance.
        """
        base_files = validated_data.pop("base_files", [])
        required_files = validated_data.pop("required_files", [])
        constraints = validated_data.pop("constraints", [])

        try:
            assignment = Assignments.objects.create(**validated_data)

            for base in base_files:
                BaseFiles.objects.create(assignment=assignment, **base)

            if not required_files:
                raise serializers.ValidationError(
                    {"required_files": "At least one required file is mandatory."}
                )
            for req in required_files:
                RequiredSubmissionFiles.objects.create(assignment=assignment, **req)

            for const in constraints:
                Constraints.objects.create(assignment=assignment, **const)

        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Assignment creation failed: {str(e)}"}
            )

        return assignment
