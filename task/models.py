from django.db import models
from django.contrib.auth.models import User

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

SEAT_CHOICES = [
    ('General', 'General'),
    ('Sleeper', 'Sleeper'),
    ('3A', '3A'),
    ('2A', '2A'),
    ('First Class', 'First Class'),
]

class Choices(models.Model):
    name = models.CharField(max_length=12, choices=SEAT_CHOICES)

    def __str__(self):
        return self.get_name_display()

class Train(models.Model):
    name = models.CharField(max_length=255)
    start = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    time = models.TimeField(default='00:00:00')
    is_active = models.BooleanField(default=False)
    operating_days = models.ManyToManyField('Day', through='Train_operating_days', related_name='trains')
    
    def available_seats(self, seat_type):
        total_seats = self.sections.filter(name__name=seat_type).count()
        booked_seats = 0
        return max(0, total_seats - booked_seats)

    def update_active_status(self):
        has_sections = bool(self.sections.count() > 0)
        if has_sections:
            available = any(self.available_seats(seat_type) > 0 for seat_type in self.sections.values_list('name__name', flat=True))
            self.is_active = available
        else:
            self.is_active = False

    
    def __str__(self):
        return self.name
    
class Train_operating_days(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.train.name} - {self.day}"

class Section(models.Model):
    name = models.ForeignKey(Choices, on_delete=models.CASCADE)
    number = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='sections')
    
    def available_seats(self, seat_type):
        total_seats = self.name.filter(name=seat_type).count()
        booked_seats = 0
        return max(0, total_seats - booked_seats)
    
class Wallet(models.Model):
    user = models.OneToOneField(User , on_delete = models.CASCADE, related_name = 'wallet')
    balance = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0)

    def __str__(self):
        return f"Wallet of {self.user.username}"