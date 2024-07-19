import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models import BaseModel
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    profile_picture = models.ImageField(_("profile picture"), upload_to="static/profile_pictures/", blank=True, null=True)
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


class FarmManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    # get user's Farm
    def get_user_farm(self, user: User):
        return self.get_queryset().filter(user=user).first()


class Farm(BaseModel):

    objects = FarmManager()

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    farm_name = models.CharField(_("farm name"), max_length=255, blank=True)
    farm_logo = models.ImageField(_("farm logo"), upload_to="static/farm_logos/", blank=True, null=True)
    tax_id = models.CharField(max_length=255, blank=True, null=True)
    farm_email = models.CharField(max_length=255)
    farm_website = models.CharField(max_length=255, blank=True, null=True)
    farm_phone_number = models.CharField(max_length=20, blank=True, null=True)
    farm_address = models.CharField(max_length=255, blank=True, null=True)
    farm_city = models.CharField(max_length=100, blank=True, null=True)
    farm_state_province = models.CharField(max_length=100, blank=True, null=True)
    farm_country = models.CharField(max_length=100, blank=True, null=True)
    farm_postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.farm_name} - {self.user.email}"
    
@receiver(post_save, sender=User)
def create_a_default_company(sender, instance: User, created, **kwargs):

    if created:
        Farm.objects.create(user=instance)

    # if user has no Farm, create a default Farm for user
    if not instance.farm_set.all():
        Farm.objects.create(user=instance)