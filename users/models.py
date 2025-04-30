from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_customer=models.BooleanField(default=False)
    is_tasker=models.BooleanField(default=False)

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Avoids clash with default auth.User.groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Avoids clash with default auth.User.user_permissions
        blank=True
    )

class Service(models.Model):
    #tasker=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    name=models.CharField(max_length=100)
    description=models.TextField(blank=True,null=True)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='images/service_images/', blank=True, null=True)

    def __str__(self):
        return self.name



    


class TaskerProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number=models.CharField(max_length=15,null=True,blank=True)
    address=models.TextField(null=True)
    bio=models.TextField(blank=True,null=True)
    profile_image=models.ImageField(upload_to='profiles/',blank=True,null=True)
    availability_start = models.TimeField(help_text="Available from (e.g. 4:00 AM)",null=True)
    availability_end = models.TimeField(help_text="Available until (e.g. 7:00 PM)",null=True)
    city = models.CharField(max_length=100,null=True)
    services=models.ManyToManyField(Service,related_name="taskers",help_text="Select the services  you provide..",)



    def __str__(self):
        return self.user.username







class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    role = models.CharField(max_length=20, default='customer')  # Add role field

    def save(self, *args, **kwargs):
        if not self.role:
            self.role = 'customer'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
