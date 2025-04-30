from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import TaskerProfile, CustomerProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "is_tasker", "is_customer")

class TaskerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskerProfile
        fields = ("phone_number", "address", "bio", "profile_image", "availability_start", "availability_end", "city")

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ("phone_number", "address", "city")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    is_tasker = serializers.BooleanField(required=False)
    is_customer = serializers.BooleanField(required=False)
    

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "is_customer", "is_tasker")

    def create(self, validated_data):
        user = User(**validated_data)  # Unpacking fields
        user.set_password(validated_data["password"])  # Set the password
        user.save()  # Save the user instance

        # Create the appropriate profile based on user type
        if user.is_tasker:
            TaskerProfile.objects.create(user=user)
        elif user.is_customer:
            CustomerProfile.objects.create(user=user)

        return user
