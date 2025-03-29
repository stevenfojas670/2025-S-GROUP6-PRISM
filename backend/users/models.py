"""User Model."""

from django.contrib.auth.models import (
    AbstractUser,
    Group,
    PermissionsMixin,
    BaseUserManager,
    Permission,
)
from django.db import models


class UserManager(BaseUserManager):
    """UserManager is a custom manager for the User model that provides methods
    for creating regular users and superusers.

    It extends the BaseUserManager class provided by Django.
    Methods:
        create_user(email, password, **extra_fields):
            Creates and returns a new user with the given email and password. Additional
            fields can be passed as keyword arguments. If a "username" is not provided in
            the extra fields, it defaults to the email address. Raises a ValueError if the
            email is not provided.
        create_superuser(email, password, **extra_fields):
            Creates and returns a new superuser with the given email and password. This
            method sets the is_admin, is_staff, and is_superuser flags to True. Additional
            fields can also be passed as keyword arguments.
    """

    # **extra field allows us to pass a dictionary with extra fields that will be inserted into hte user
    # example first_name, last_name etc
    def create_user(self, email, password, **extra_fields):
        """Creates and returns a new user with the given email and password.

        Args:
            email (str): The email address of the user. This is required.
            password (str): The password for the user. This will be hashed before saving.
            **extra_fields: Additional fields to include when creating the user. If a
                            "username" is not provided in extra_fields, it will default
                            to the email address.
        Raises:
            ValueError: If the email is not provided.
        Returns:
            User: The created user instance.
        """
        if not email:
            raise ValueError("Users must have an email address")

        # Automatically set username to email if the username was not provided
        # in the create_user call (in the extra fields)
        if not extra_fields.get("username"):
            extra_fields["username"] = email

        # django modelbase user manager you call self.model and its like
        # creating a new User (our defined User class)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # we hash the password cuz we cant just save the password in the
        # databse
        user.set_password(password)
        # self._db supports adding multiple databse, best practice but we wont
        # do this tho
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates and returns a superuser with the given email, password, and
        extra fields.

        A superuser is a user with elevated permissions, including admin, staff,
        and superuser privileges.

        Args:
            email (str): The email address of the superuser.
            password (str): The password for the superuser.
            **extra_fields: Additional fields to set on the superuser.

        Returns:
            user: The created superuser instance.
        """
        user = self.create_user(email, password, **extra_fields)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser, PermissionsMixin):
    """User Model This model represents a custom user in the system, extending
    Django's AbstractUser and PermissionsMixin to provide additional
    functionality and customization.

    Attributes:
        email (EmailField): The unique email address of the user, used as the username for authentication.
        first_name (CharField): The first name of the user, with a maximum length of 50 characters.
        last_name (CharField): The last name of the user, with a maximum length of 50 characters.
        is_admin (BooleanField): A flag indicating whether the user has administrative privileges. Defaults to False.
        objects (UserManager): The custom manager for the User model.
        USERNAME_FIELD (str): Specifies the field to be used as the unique identifier for authentication. Set to "email".
        REQUIRED_FIELDS (list): A list of fields required when creating a user. Includes "first_name" and "last_name".
        groups (ManyToManyField): A many-to-many relationship to the Group model, with a custom related name "custom_user_set".
        user_permissions (ManyToManyField): A many-to-many relationship to the Permission model, with a custom related name
            "custom_user_permissions_set".
    Methods:
        __str__(): Returns a string representation of the user in the format "FirstName LastName (Email)".
    """

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)

    # linking the user manager to this custom user model
    objects = UserManager()

    # default behavior is to create a username; here the username is the email
    # field
    USERNAME_FIELD = "email"
    # email is by default required; add any other required fields here
    REQUIRED_FIELDS = ["first_name", "last_name"]

    groups = models.ManyToManyField(
        Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permissions_set", blank=True
    )

    def __str__(self):
        """Returns a string representation of the user instance.

        The string includes the user's first name, last name, and email
        in the format: "FirstName LastName (email@example.com)".

        Returns:
            str: A formatted string representing the user.
        """
        return f"{self.first_name} {self.last_name} ({self.email})"
