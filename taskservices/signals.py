from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomerProfile
from .models import Booking, Notification
from django.contrib.auth.models import User 
from django.contrib.auth import get_user_model




# User = get_user_model()
def notify_user(user, message,booking=None):
    """Create a notification for the user."""
    Notification.objects.create(recipient=user, message=message,booking=booking)

def notify_tasker(tasker, message,booking=None):
    """Create a notification for the tasker."""
    Notification.objects.create(recipient=tasker.user, message=message,booking=booking)

@receiver(post_save, sender=Booking)
def create_booking_notification(sender, instance, created, **kwargs):
    if created:  # Check if the Booking instance was created
        print("Booking created, sending notifications.")
        
        # Ensure we have the correct instance types
        print(f"Type of tasker: {type(instance.tasker)}")  # Should show TaskerProfile
        print(f"Type of customer: {type(instance.customer)}")  # Should show CustomerProfile
        
        # Notify user and tasker about the booking
        customer_message = f"You have booked {instance.tasker.user.username} for {instance.service.name}"
        notify_user(instance.customer.user, customer_message,booking=instance)  # Ensure this is a User instance

        tasker_message = f"You have a booking request from {instance.customer.user.username} for {instance.service.name}"
        notify_tasker(instance.tasker, tasker_message,booking=instance)  # Ensure this is a TaskerProfile instance

@receiver(post_save, sender=Booking)
def accept_booking_notification_for_customer(sender, instance, created, **kwargs):
    if instance.status == "accept":
        Notification.objects.create(
            recipient=instance.customer.user,
            message=f"Your booking with {instance.tasker.user.username} has been accepted.",
            booking=instance  # ✅ link booking
)

        # Notification.objects.create(
        #     recipient=instance.customer.user,
        #     message=f"Your booking with {instance.tasker.user.username} has been accepted.",
        #     created_date=timezone.now(),
        #     is_read=False
        # )

@receiver(post_save, sender=Notification)
def notify_customer(sender, instance, created, **kwargs): #notify the customer new price suggested by takser
    if created and "suggested a new price" in instance.message:
       
        print(f"Notification sent to {instance.recipient} about the price suggestion.")

@receiver(post_save,sender=Booking) #notify the tasker,customer accepted suggested price 
def notify_tasker_on_price_acceptance(sender,instance,created,**kwargs):

    if instance.price_accepted:
        Notification.objects.create(
            recipient=instance.tasker.user,
            message=f"The customer has accepted your suggested price of {instance.confirmed_price}."
        )
