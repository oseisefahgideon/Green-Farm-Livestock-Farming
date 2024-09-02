from django.db import models
from base.models import BaseModel

from django.db import models
from django.conf import settings
from account.models import Farm  

class Livestock(BaseModel):
    LIVESTOCK_STATUS_CHOICES = [
        ("Active", "Active"),
        ("Sold", "Sold"),
        ("Deceased", "Deceased"),
    ]
    
    ANIMAL_TYPE_CHOICES = [
        ("Cow", "Cow"),
        ("Sheep", "Sheep"),
        ("Pig", "Pig"),
        ("Goat", "Goat"), 
        ("Horse", "Horse"),
        ("Chicken", "Chicken"),
        ("Duck", "Duck"),
        ("Turkey", "Turkey"),
        ("Rabbit", "Rabbit"),
        ("Other", "Other"),
    ]
    
    ACQUISITION_METHOD_CHOICES = [
        ("Purchase", "Purchase"),
        ("Gift", "Gift"),
        ("Trade", "Trade"),
        ("Breeding", "Breeding"),
        ("Other", "Other"),
    ]
    
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    animal_type = models.CharField(max_length=50, choices=ANIMAL_TYPE_CHOICES)
    breed = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=True, null=True)
    tag_number = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Tag number can be null initially
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    acquisition_date = models.DateField()
    acquisition_method = models.CharField(max_length=50, choices=ACQUISITION_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=LIVESTOCK_STATUS_CHOICES)
    current_weight = models.FloatField()
    current_age = models.IntegerField()
    photo = models.ImageField(upload_to="livestock_photos/", blank=True, null=True)

    def __str__(self):
        return f"{self.animal_type} - {self.tag_number}"

    def save(self, *args, **kwargs):
        if not self.tag_number:
            self.tag_number = self.generate_tag_number()
        super().save(*args, **kwargs)

    def generate_tag_number(self):
        return f"{self.animal_type[:3].upper()}{self.date_of_birth.strftime('%Y%m%d')}{self.id or '001'}"


class FeedingRecord(BaseModel):
    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE)
    feed_type = models.CharField(max_length=100)
    quantity = models.FloatField()
    unit = models.CharField(max_length=10)  # kg, lbs, etc.
    administered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Feeding for {self.livestock.tag_number} on {self.feeding_date}"


class HealthRecord(BaseModel):
    RECORD_TYPE_CHOICES = [
        ("Illness", "Illness"),
        ("Vaccination", "Vaccination"),
        ("Routine Check", "Routine Check"),
    ]

    livestock = models.ForeignKey(Livestock, on_delete=models.CASCADE)
    record_type = models.CharField(max_length=50, choices=RECORD_TYPE_CHOICES)
    date = models.DateField()
    description = models.TextField()
    diagnosis = models.CharField(max_length=255, blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    medication = models.CharField(max_length=255, blank=True, null=True)
    dosage = models.CharField(max_length=100, blank=True, null=True)
    administered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    veterinarian_name = models.CharField(max_length=100, blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    outcome = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Health Record for {self.livestock.tag_number} on {self.date}"
