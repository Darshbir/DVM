from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from .models import *

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

post_save.connect(create_user_wallet, sender=User)

@receiver(pre_delete, sender=Booking)
def refund_on_booking_deletion(sender, instance, **kwargs):
    refunded_amount = instance.num_seats * instance.section.price
    instance.user.wallet.balance += refunded_amount
    instance.user.wallet.save()

pre_delete.connect(refund_on_booking_deletion, sender=Booking)