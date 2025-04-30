from django.db import models
from users.models import *


class Booking(models.Model):
	customer=models.ForeignKey(CustomerProfile,related_name="customer_bookings",on_delete=models.CASCADE)
	tasker=models.ForeignKey(TaskerProfile,related_name="tasker_bookings",on_delete=models.CASCADE)
	service=models.ForeignKey(Service,related_name="services_booking",on_delete=models.CASCADE)
	date_booking=models.DateField()
	start_time=models.TimeField()
	end_time=models.TimeField()
	status = models.CharField(
    max_length=50,  # Keyword argument for max length
    choices = (
    ('ACCEPT', 'Accept'),
    ('PENDING', 'Pending'),
    ('REJECT', 'Reject'),
    ('COMPLETED', 'Completed'),
),
    default="PENDING"  # Keyword argument for the default value
)

	tasker_price_suggestion=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	confirmed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	price_accepted=models.BooleanField(default=False)
	message = models.TextField(null=True, blank=True)


	def __str__(self):
		return f"Booking: {self.customer.user.username} with {self.tasker.user.username} for {self.service.name}"

@property
def service_price(self):
    return self.service.price

@property
def final_price(self):
    return self.confirmed_price if confirmed_price else service_price


class Notification(models.Model):
	recipient=models.ForeignKey(User,related_name="notifications",on_delete=models.CASCADE)
	message=models.TextField()
	created_date=models.DateTimeField(auto_now_add=True)
	is_read= models.BooleanField(default=False)
	booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL)
  


	def __str__(self):
		return f"Notification for {self.recipient.username}:{self.message}"
	



class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='given_reviews')
    tasker = models.ForeignKey(TaskerProfile, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review ({self.rating}★) by {self.customer.user.username} for {self.tasker.user.username}"


    




