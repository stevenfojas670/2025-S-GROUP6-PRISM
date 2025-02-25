"""
User Model.
"""
from django.contrib.auth.models import AbstractUser, Group, PermissionsMixin, BaseUserManager, Permission
from django.db import models

class UserManager(BaseUserManager):
    """Manager class for User model."""
    #**extra field allows us to pass a dictionary with extra fields that will be inserted into hte user
    #example first_name, last_name etc
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        # Automatically set username to email if the username was not provided
        #in the create_user call (in the extra fields)
        if not extra_fields.get('username'):
            extra_fields['username'] = email

        #django modelbase user manager you call self.model and its like creating a new User (our defined User class)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        #we hash the password cuz we cant just save the password in the databse
        user.set_password(password)
        #self._db supports adding multiple databse, best practice but we wont do this tho
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractUser, PermissionsMixin):
    """Custom User model for Professors"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)

    # linking the user manager to this custom user model
    objects = UserManager()

    # default behavior is to create a username; here the username is the email field
    USERNAME_FIELD = 'email'
    # email is by default required; add any other required fields here
    REQUIRED_FIELDS = ['first_name', 'last_name']

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

