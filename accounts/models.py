from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.constraints import CheckConstraint

"""
Defines the custom User model and manager for the application.
We use a custom User model to use 'email' as the primary identifier instead of a username.
"""

class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    Handles creation of regular users and superusers using email addresses.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a new User with the given email and password.

        Args:
            email (str): Users email address (required).
            password (str): Users password (optional).
            **extra_fields: Additional fields for the user model.

        Returns:
            User: The created user instance.

        Raises:
            ValueError: If the email is not provided.
        """
        if not email:
            raise ValueError("The email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a Superuser with the given email and password.

        This method sets is_staff and is_superuser to True by default.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model where email is the unique identifier.

    This model replaces the default Django User model. It includes
    basic profile fields like first_name, last_name, and gender.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Others'),
    ]

    # Email is the primary identifier; db_index=True is implicit for unique=True
    email = models.EmailField(unique=True, max_length=255)
    
    # Adding db_index for fast lookups by name
    first_name = models.CharField(max_length=50, db_index=True)
    last_name = models.CharField(max_length=50, db_index=True)
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        # SQL Level constraints
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(email__contains='@'),
                name="valid_email_check"
            ),
        ]

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.lower()