from django.contrib import admin
from .models import *
from .models import Booking,Review

class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_username', 'tasker', 'service', 'date_booking', 'start_time', 'end_time', 'status')

    def customer_username(self, obj):
        return obj.customer.user.username  # Access username through the related User model
    customer_username.short_description = 'Customer Username'  # Label for the column


admin.site.register(Booking, BookingAdmin)
admin.site.register(Notification)
admin.site.register(Review)
