# Generated by Django 4.2.7 on 2024-01-06 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0010_passenger_seat_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passenger',
            name='seat_num',
        ),
        migrations.AlterField(
            model_name='passenger',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=10),
        ),
    ]