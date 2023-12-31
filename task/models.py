from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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
    ('General','General'),
    ('Sleeper', 'Sleeper'),
    ('3A' , '3A'),
    ('2A' , '2A'),
    ('First Class' , 'First Class'),
    ]

class choices(models.Model):
    name = models.CharField(max_length=12, choices=SEAT_CHOICES)

    def __str__(self):
        return self.get_name_display()
    
class Train(models.Model):
    name = models.CharField(max_length=255)
    start = models.CharField(max_length = 100)
    destination = models.CharField(max_length = 100)
    operating_days = models.ManyToManyField(Day)
    time = models.TimeField(default='00:00:00')
    is_active = models.BooleanField(default = True)
    def available_seats(self , seat_type):
        total_seats = 0

        for section in self.sections.all():
            total_seats += section.available_seats(seat_type)
        
        return total_seats
    
    def save(self, *args, **kwargs):
        available = any(self.available_seats(seat_type) > 0 for seat_type in ['General', 'Sleeper', '3A', '2A', 'First Class'])
        self.is_active = available
        super().save(*args, **kwargs)


class sections(models.Model):
    name = models.ManyToManyField(choices)
    number = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    train =  models.ForeignKey(Train , on_delete = models.CASCADE)
    
    def available_seats(self , seat_type):
        total_seats = self.name.filter(name=seat_type).count()

        booked_seats = 0

        return (total_seats-booked_seats)

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('Required field')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(email, password, **extra_fields)

# class CustomUser(AbstractBaseUser):
#     email = models.EmailField(unique=True)
#     wallet = models.OneToOneField('Wallet', on_delete=models.CASCADE, null=True, blank=True)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'

#     def __str__(self):
#         return self.email

# class Wallet(models.Model):
#     balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

#     def __str__(self):
#         return f'Wallet for User: {self.user.email}'