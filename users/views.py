from django.shortcuts import render,redirect,get_object_or_404
from  rest_framework.permissions  import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .serializers import *
from .models import *
from rest_framework import generics
from rest_framework import status
from django.contrib.auth import logout
from django.http import JsonResponse
import requests
from django.conf import settings
import json  
from .forms import ProfileForm,CustProfileForm
import jwt
from django.conf import settings
from users.auth_utils import get_tokens_for_user  # Ensure correct import path
from django.contrib.auth import login
import requests
from django.contrib.auth.decorators import login_required
from taskservices.models import *
from datetime import date, timedelta
from django.utils import timezone







def decode_token(token):
	try:
		decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
		print("Decoded Token:", decoded)  # Debugging print
		return decoded
	except jwt.ExpiredSignatureError:
		print("Token has expired")  # Debug
		return None
	except jwt.InvalidTokenError:
		print("Invalid token")  # Debug
		return None




REGISTER_API_URL='http://localhost:8000/api/register/'
LOGIN_API_URL='http://127.0.0.1:8000/api/login/'



def task_register(request):
	if request.method == "POST":
		username = request.POST["username"]
		email = request.POST["email"]
		password = request.POST["password"]
		is_customer = False
		is_tasker = True

		data = {
			"username": username,
			"email": email,
			"password": password,
			"is_tasker": is_tasker,
			"is_customer": is_customer,
		}
		# print("data-", data)

		try:
			response = requests.post(REGISTER_API_URL, json=data)
			print("Error Response:", response.content)  # Print the response content for debugging

			# Ensure the response status code is 201
			if response.status_code == 201:
				# print(f"Response Status Code: {response.status_code}")
				# print(f"Response Content: {response.content}")
				
				# Attempt to parse the response as JSON
				try:
					response_data = response.json()  # This should return a dict if the response is JSON
					# print("Parsed Response Data:", response_data)
					user_id = response_data.get('id')  # Retrieve the user id from response
					return redirect('tasker_profile', user_id=user_id)
				except ValueError as e:
					print(f"Error parsing JSON: {e}")
					return render(request, "auth/tasker_register.html", {"error": "Invalid server response."})

			else:
				# If the response was not successful, handle errors
				try:
					error_data = response.json()  # Attempt to get error data
				except ValueError:
					error_data = {"invalid server response..!"}

				return render(request, "auth/tasker_register.html", {"error": error_data})

		except Exception as e:
			print(f"Error occurred: {e}")
			return render(request, "auth/tasker_register.html", {"error": "An error occurred while registering."})

	return render(request, "auth/tasker_register.html")




def customer_register(request):

	if request.method == "POST":
		username=request.POST["username"]
		email=request.POST["email"]
		password=request.POST["password"]
		is_customer=True
		is_tasker=False

		data={"username":username,
		"email":email,
		"password":password,
		"is_tasker":is_tasker,
		"is_customer":is_customer

		}
		#   print("data-",data)

		try:
			response=requests.post(REGISTER_API_URL,json=data)

			if response.status_code==201:
				try:
					response_data = response.json()  # This should return a dict if the response is JSON
					user_id = response_data.get('id')  # Retrieve the user id from response
					return redirect('customer_profile', user_id=user_id)
					
				except Exception as e:
					print(f"Error parsing JSON: {e}")
					return render(request, "auth/cutomer_register.html", {"error": "Invalid server response."})
				
			else:
				try:
					error_data=response.json()

				except ValueError:
					error_data={"error":"the invlalid server response..!"}

				return render(request,"auth/customer_register.html",{'error':error_data})

		except Exception as e:
			print(f"error occured at{e}")
			return render(request,"auth/customer_register.html",{'error':"an error occured somewhere..!"})

	return render(request,"auth/customer_register.html")




def customerlogin_view(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')
		
		# Ensure username and password are provided
		if not username or not password:
			return render(request, "auth/customer_login.html", {"error": "Username and password are required"})
		
		data = {
			"username": username,
			"password": password,
		}

		user = authenticate(username=data['username'], password=data['password'])
		if user is not None:
			# Log the user in to create a session
			login(request, user)
			# print("Logged in Django user:", request.user)  # Debugging print
		
			try:
				# Send a POST request to the login API
				response = requests.post(LOGIN_API_URL, json=data)
				print("API response status:", response.status_code)

				if response.status_code == 200:
					tokens = response.json()
					access_token = tokens.get('access')
					refresh_token = tokens.get('refresh')
					print("Logged in Django users:", request.user)
					# Redirect to landing page
					response = redirect('landing')
					
					# Set cookies securely (use secure=True if using HTTPS)
					response.set_cookie("access_token", access_token, httponly=True, secure=request.is_secure())
					response.set_cookie("refresh_token", refresh_token, httponly=True, secure=request.is_secure())
					return response

				else:
					error_data = response.json().get("error", "Invalid credentials")
					return render(request, "auth/customer_login.html", {"error": error_data})
			
			except requests.RequestException as e:
				print(f"Server error occurred: {e}")
				return render(request, "auth/customer_login.html", {"error": "Server error. Please try again later."})
		else:
			return render(request, "auth/customer_login.html", {"error": "Invalid username or password"})

	# If GET request, render the login page
	return render(request, "auth/customer_login.html")



def taskerlogin_view(request):


	if request.method=="POST":
		username=request.POST['username']
		password=request.POST['password']
		data={"username":username,
  
		"password":password,

		}
		print("data-",data)
		user = authenticate(username=data['username'], password=data['password'])
		if user is not None:
			# Log the user in to create a session
			login(request, user)
		try:
			response=requests.post(LOGIN_API_URL,json=data)
			if response.status_code==200:
				tokens = response.json()
				access_token=tokens['access']
				refresh_token=tokens['refresh']
				response=redirect('taskerprofile')
				response.set_cookie("access_token",access_token,httponly=True)
				response.set_cookie("refresh_token",refresh_token,httponly=True)
				return response
			else:
				try:
					error_data=response.json()
				except ValueError:
					error_data={"error":"invlalid credentials..!"}

				return render(request,"auth/tasker_login.html",error_data)


		except Exception as e:
			print(f"error occured in server as{e}")
			return render(request,"auth/tasker_login.html",{'error':"invalid credentials"})
		

	return render(request,"auth/tasker_login.html")



def logout_view(request):
	try:
		refresh_token=request.COOKIES.get('refresh_token')
		if refresh_token:
			token =RefreshToken(refresh_token)
			token.blacklist()

	except Exception as e:
		print("Error for deleting the cookies",e)
	response=redirect('home')
	response.delete_cookie("access_token")
	response.delete_cookie("refresh_token")

	logout(request)

	return response


def landingcustomer(request):
	print(request.user)
	services=Service.objects.all()
	context={"services":services}
	return render(request,'customer/cust_landing.html',context)

def home(request):
	return render(request,'index.html')

def servicespage(request):
	return render(request,'services.html')
def aboutspage(request):
	return render(request,'about_us.html')
def contacus(request):
	return render(request,'contact.html')



def tasker_profile(request,user_id):
	
		tasker_profile,created=TaskerProfile.objects.get_or_create(user_id=user_id)
		if request.method=="POST":
			form=ProfileForm(request.POST,request.FILES,instance=tasker_profile)
			if form.is_valid():
				form.save()
				return redirect('success')
			else:
				print("errors:",form.errors)
		else:

			form=ProfileForm(instance=tasker_profile)

		return render(request,"tasker/tasker_profile.html",{"form":form})


def customer_profile(request,user_id):
	
		customer_profile,created=CustomerProfile.objects.get_or_create(user_id=user_id)
		if request.method=="POST":
			form=CustProfileForm(request.POST,request.FILES,instance=customer_profile)
			if form.is_valid():
				form.save()
				return redirect('landing')
			else:
				print("errors:",form.errors)
		else:

			form=CustProfileForm(instance=customer_profile)

		return render(request,"customer/customer_profile.html",{"form":form})


def singlecust(request,object_id):
	service=Service.objects.get(pk=object_id)
	taskers = TaskerProfile.objects.filter(services=service)
	context={"service":service,"taskers":taskers}
	return render(request,"customer/cust_single.html",context)


def success(request):
	return render(request,"success.html")


User = get_user_model()

class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
	permission_classes = [IsAuthenticated]

	def get_object(self):
		# Check if the user is a tasker or customer and return the appropriate profile
		user = self.request.user
		if user.is_tasker:
			return TaskerProfile.objects.get(user=user)
		elif user.is_customer:
			return CustomerProfile.objects.get(user=user)
		return None  # Handle the case where the user has no profile

	def get_serializer_class(self):
		user = self.request.user
		if user.is_tasker:
			return TaskerProfileSerializer
		elif user.is_customer:
			return CustomerProfileSerializer
		return super().get_serializer_class()

class LogoutView(generics.GenericAPIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		try:
			refresh_token = request.data["refresh_token"]
			token = RefreshToken(refresh_token)  # Pass the actual refresh token
			token.blacklist()
			return Response(status=205)  # Use 205 Reset Content for a successful logout
		except Exception as e:
			print(f"Error occurred during logout: {e}")
			return Response(status=400)


@login_required
def tasker_profile_view(request):
    tasker = get_object_or_404(TaskerProfile, user=request.user)
    all_customers=CustomerProfile.objects.all()
    today = date.today()
    tomorrow = today + timedelta(days=1)
    now = timezone.localtime().time()
	

    # Notifications (latest 3)
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_date')[:3]
    notifications_count = notifications.count()

    # Handle marking a booking as completed
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id, tasker=tasker)

        booking.status = 'COMPLETED'
        booking.save()
		

        # Notify customer
        Notification.objects.create(
            recipient=booking.customer.user,
            message=f"{tasker.user.username} has completed the task '{booking.service.name}'.",
            booking=booking
        )

        return redirect('taskerprofile')

    # Show all accepted bookings from today onwards
    today = date.today()
    bookings = Booking.objects.filter(
        tasker=tasker,
        date_booking__gte=today,
        status='ACCEPT'
    ).order_by('date_booking', 'start_time')

    # No status logic needed — just pass bookings
    feed_items = [{'booking': booking, 'status': "Accepted"} for booking in bookings]
	   
 # ✅ NEW: Dynamically fetch completed tasks (before today or earlier today)
    completed_tasks = Booking.objects.filter(
        tasker=tasker,
        status='COMPLETED'
    ).order_by('-date_booking', '-end_time')

    # ✅ NEW: Order completed tasks latest first
    # completed_tasks = completed_tasks.order_by('-date_booking', '-end_time')
    reviews = Review.objects.filter(tasker=tasker).order_by('-created_at')

    context = {
        'tasker': tasker,
        'notifications': notifications,
        'notifications_count': notifications_count,
        'feed_items': feed_items,
		'completed_tasks': completed_tasks,
		'reviews': reviews,
		'all_customers':all_customers,
    }

    return render(request, 'tasker/profiletasker.html', context)


@login_required
def notification_all(request):
	notifications = Notification.objects.filter(recipient=request.user).order_by('-created_date')
	context={"notifications":notifications}
	return render(request,"tasker/allnotifications.html",context)
