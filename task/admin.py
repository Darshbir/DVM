from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Day)
admin.site.register(Section)
admin.site.register(Choices)
admin.site.register(Train_operating_days)

def delete_selected_trains(modeladmin, request, queryset):
    for train in queryset:
        bookings_to_refund = Booking.objects.filter(section__train=train)

        for booking in bookings_to_refund:
            refunded_amount = booking.num_seats * booking.section.price
            booking.user.wallet.balance += refunded_amount
            booking.user.wallet.save()

        train.delete()


delete_selected_trains.short_description  = "Delete Selected Trains"

class TrainAdmin(admin.ModelAdmin):
    actions = [delete_selected_trains]

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(Train, TrainAdmin)