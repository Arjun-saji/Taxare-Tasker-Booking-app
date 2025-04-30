from django.contrib import admin
from .models import *

admin.site.register(TaskerProfile)
admin.site.register(CustomerProfile)
admin.site.register(User)
admin.site.register(Service)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']


# Register your models here.

