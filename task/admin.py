from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Day)
admin.site.register(Train)
admin.site.register(Section)
admin.site.register(Choices)
admin.site.register(Train_operating_days)