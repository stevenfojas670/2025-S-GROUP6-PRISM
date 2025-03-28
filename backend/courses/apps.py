from django.apps import AppConfig


class CoursesConfig(AppConfig):
    """
    Django application configuration class for the 'courses' app.

    This class defines the default settings for the 'courses' app, including
    the default type of primary key field for models and the app's name.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "courses"
