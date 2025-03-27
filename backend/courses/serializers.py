
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


# Serializer stuff lets us send data to frontend with API responses. 
# Also validates incoming JSON data and helps by converting to an enrollment object when creating/updating records.
# Similar structure to PCSSerializer
class EnrollmentSerializer(serializers.ModelSerializer):
    """Enrollment Model Serializer."""
    
    # For read operations, show full student/class/semester details. without this, the data thats returned for these would be just ids.
    # This makes the data quickly readable for frontend.
    # This works bc frontend probably just needs these names, and not the full detailes about each object. 
    # It reduces db queries => improved performance
    student = serializers.StringRelatedField(read_only=True)
    class_instance = serializers.StringRelatedField(read_only=True)
    semester = serializers.StringRelatedField(read_only=True)

    # Just accepting ids for writes. Same reasoning as PCSSerializer. i.e. he client can just specify a student_id, instead
    #of an entire student object. It also maps the student_id to the actual 'student' field in the enrollment (source='student')
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Student.objects.all(), 
        source='student', 
        write_only=True
    )
    class_instance_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Class.objects.all(), 
        source='class_instance', 
        write_only=True
    )
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Semester.objects.all(), 
        source='semester', 
        write_only=True
    )

    # This gives frontend requests full details of student, class, and semester (rather than just ids)
    # I think the frontend can now just specify a student_id { "student_id": 1 }, instead of nesting a full student because of this.
    class Meta:
        model = models.Enrollment
        fields = [
            'id',
            'student',
            'student_id',
            'class_instance',
            'class_instance_id',
            'semester',
            'semester_id',
            'enrolled_date',
            'dropped',
            'dropped_date'
        ]