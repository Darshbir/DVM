# Generated by Django 4.2.7 on 2024-01-19 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0017_alter_section_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='booked_seats',
            field=models.PositiveIntegerField(default=0),
        ),
    ]