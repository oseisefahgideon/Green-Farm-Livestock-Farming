import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        if not password:
            raise ValueError(_("The Password must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        
        # Create a farm for the new user
        Farm.objects.create(user=user)
        
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_("user email"), max_length=254, unique=True)

    first_name = models.CharField(_("first name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)
    profile_picture = models.ImageField(_("profile picture"), upload_to="profile_pictures/", blank=True, null=True)
    phone_number = models.CharField(_("phone number"), max_length=20, blank=True)
    date_of_birth = models.DateField(_("date of birth"), null=True, blank=True)
    gender = models.CharField(_("gender"), max_length=10, blank=True)
    address = models.CharField(_("address"), max_length=255, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state_province = models.CharField(_("state/province"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    postal_code = models.CharField(_("postal code"), max_length=20, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

class Farm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farm')
    farm_name = models.CharField(_("farm name"), max_length=255, blank=True)
    location = models.CharField(_("location"), max_length=255, blank=True)

    def __str__(self):
        return f"{self.farm_name} - {self.user.email}"