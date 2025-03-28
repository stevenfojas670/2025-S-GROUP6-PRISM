from django.apps import AppConfig


class DataIngestionConfig(AppConfig):
    """Configuration class for the 'data_ingestion' application.

    This class defines the default settings for the application, including
    the default primary key field type and the application name.

    Attributes:
        default_auto_field (str): Specifies the type of primary key field to use
            for models in this application. Defaults to "django.db.models.BigAutoField".
        name (str): The name of the application. Used by Django to identify the app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "data_ingestion"
