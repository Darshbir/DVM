from django.db import models
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.
DAYS_OF_WEEK_CHOICES = [
    ('Mon', 'Monday'),
    ('Tue', 'Tuesday'),
    ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'),
    ('Fri', 'Friday'),
    ('Sat', 'Saturday'),
    ('Sun', 'Sunday'),
]

class Day(models.Model):
    name = models.CharField(max_length=3, choices=DAYS_OF_WEEK_CHOICES)

    def __str__(self):
        return self.get_name_display()

class Train(models.Model):
    name = models.CharField(max_length=255)
    start = models.CharField(max_length = 100)
    destination = models.CharField(max_length = 100)
    seats = models.IntegerField()
    price = models.IntegerField()
    operating_days = models.ManyToManyField(Day)

# class CustomUser(AbstractBaseUser):
#     wallet = models.IntegerField()
#     first_name = models.CharField(max_lenght = 100)
#     last_name = models.CharField(max_length = 100)
#     username = models.CharField(max_length = 25, unique = True)
#     USERNAME_FIELD = ['username']

#     REQUIRED_FIELDS = []

    