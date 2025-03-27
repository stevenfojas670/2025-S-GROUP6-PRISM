"""
Courses Models Serializers.
"""
from rest_framework import serializers
from courses import models
from users import serializers as user_serializer

class ProfessorSerializer(serializers.ModelSerializer):
    """Professor Model Serializer."""
    user = user_serializer.UserSerializer(read_only=True)
    class Meta:
        model = models.Professor
        fields = "__all__"

#create() and update() methods are already implemented here by default
class ClassSerializer(serializers.ModelSerializer):
    """Class Model Serializer."""
    class Meta:
        model = models.Class
        fields = ['name']

class SemesterSerializer(serializers.ModelSerializer):
    """Semester Model Serializer."""
    class Meta:
        model = models.Semester
        fields = ['name']

class ProfessorClassSectionSerializer(serializers.ModelSerializer):
    """ProfessorClassSection Model Serializer."""
    # For read operations: show nested details
    semester = SemesterSerializer(read_only=True)
    class_instance = ClassSerializer(read_only=True)

    # For write operations: accept only IDs
    #since these are nested object its easier to simply declare them like so,
    #this will allow our client to specify the primary key (id) of the given fields
    #in their request to create new instances of ProffClassSection in the databse
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Semester.objects.all(),
        source='semester',
        write_only=True
    )
    class_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Class.objects.all(),
        source='class_instance',
        write_only=True
    )
    professor_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Professor.objects.all(),
        source='professor',
        write_only=True
    )
    class Meta:
        model = models.ProfessorClassSection
        fields = [
            'section_number',
            'semester',
            'semester_id',
            'class_instance',
            'class_instance_id',
            'professor_id'
        ]