from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from users.models import *
from django.db.models import Q
import logging
from .signals import notify_user, notify_tasker
from users.views import *
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from datetime import date,timedelta
from taskservices.models import Booking 
from users.models import TaskerProfile
from django.http import HttpResponse
from .models import Review
from payments.models import *
from django.db.models import Avg



# Set up logging
logger = logging.getLogger(__name__)

def taskfilter_view(request,service_id):
	service=Service.objects.get(id=service_id)
	taskers=TaskerProfile.objects.filter(services=service)

	start_time=request.GET.get("start_time")
	end_time=request.GET.get("end_time")
	location=request.GET.get("location")

	if start_time and end_time:
		logger.info("Filtered taskers by location: %s", taskers)
		tasker=taskers.filter(Q(availability_start__lte=start_time),Q(availability_end__gte=end_time))
		
	if location:
		tasker=taskers.filter(city=location)
		logger.info("Filtered taskers by location: %s", taskers)

	tasker_list = []
	for tasker in taskers:
		# reviews = Review.objects.filter(tasker=tasker)
		avg_rating = Review.objects.filter(tasker=tasker).aggregate(avg=Avg('rating'))['avg']
		tasker_list.append({
			'tasker': tasker,
			'average_rating': round(avg_rating, 1) if avg_rating else 'No ratings'
		})


	context={
		# "tasker":tasker,
		"service_id":service_id,
		"service": service,
		"tasker_list": tasker_list,
		
		
		}

	logger.info("Context prepared for rendering: %s", context)
	

	return render(request,"customer/cust_single.html",context)


@login_required
def book_service(request, tasker_id, service_id): #booking service from customer to the tasker
	tasker = get_object_or_404(TaskerProfile, id=tasker_id)
	service = get_object_or_404(Service, id=service_id)

	if request.method == "POST":
		date_booking = request.POST.get("date_booking")
		start_time = request.POST.get("start_time")
		end_time = request.POST.get("end_time")
		message = request.POST.get("message") 
		tasker_price_suggestion = request.POST.get("tasker_price_suggestion")
		customer_profile = get_object_or_404(CustomerProfile, user=request.user)
		
		print(f"Customer Profile User: {customer_profile.user}")
		print(f"Tasker User: {tasker.user}")
  
		try:
			# Create the booking
			booking = Booking.objects.create(
				customer=customer_profile,
				date_booking=date_booking,
				start_time=start_time,
				end_time=end_time,
				tasker_price_suggestion=tasker_price_suggestion,
				tasker=tasker,
				service=service,
				message=message
			)
			print(f"Type of tasker: {type(tasker)}")  # Should show TaskerProfile
			print(f"Type of customer: {type(customer_profile)}")  # Should show CustomerProfile

			return redirect("home")

		except Exception as e:
			print(f"Error creating booking: {e}")  # Log the exception
			# Optionally, you could handle the error more gracefully here, e.g., by showing an error message.

	context = {"tasker": tasker, "service": service}
	return render(request, "customer/booking_service.html", context)
	
@csrf_exempt
@login_required
def mark_notification_as_read(request, notification_id):
	print(f"Marking notification {notification_id} as read")
	notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
	notification.is_read = True  # Mark as read
	notification.save()
	return redirect('all_notifications')



@login_required
def profile_customer(request):  # Unified customer profile view
    customer = get_object_or_404(CustomerProfile, user=request.user)

    all_bookings = Booking.objects.filter(customer=customer)
    total_bookings = all_bookings.count()
    completed_bookings = all_bookings.filter(status__iexact='COMPLETED').count()
    total_reviews = Review.objects.filter(customer=customer).count()

    # Recent bookings
    recent_bookings = Booking.objects.filter(
        customer=customer
    ).order_by('-date_booking')[:10]

    # Payment history
    payments = Payment.objects.filter(
        customer=customer
    ).order_by('-created_at')[:10]

    # Reviews made by the customer
    reviews = Review.objects.filter(
        customer=customer
    ).order_by('-created_at')

    # Accepted notifications
    accepted_notifications = Notification.objects.filter(
        recipient=request.user,
        message__icontains="accepted"  # Adjust keyword if needed
    ).order_by('-created_date')[:3]

    notifications_count = accepted_notifications.count()

    # Booking status formatting
    booking_list = []
    for booking in recent_bookings:
        if booking.status.lower() == 'completed':
            status_display = 'Completed'
        elif booking.status.lower() == 'accept':
            status_display = 'Pending'
        else:
            status_display = booking.status.capitalize()

        booking_list.append({
            'booking': booking,
            'status': status_display
        })

    context = {
        'customer': customer,
        'recent_bookings': booking_list,
        'payments': payments,
        'reviews': reviews,
        'notifications': accepted_notifications,
        'notifications_count': notifications_count,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'total_reviews': total_reviews,
    }

    return render(request, 'customer/profilecustomer.html', context)


@login_required
def accept_booking_tasker(request,booking_id):  #tasker accepting the request from the customer
	booking=get_object_or_404(Booking, id=booking_id)
	if booking.tasker.user!= request.user:
		return redirect("all_notifications")

	booking.status="ACCEPT"
	booking.save()


	Notification.objects.create(
		recipient=booking.customer.user,
		message=f"Your booking with {booking.tasker.user.username} has been accepted.",
		created_date=timezone.now(),
		is_read=False,
		booking=booking 
	)
	
	return redirect("taskerprofile")

@login_required
def cust_notification_all(request): #to get all notifications from tasker to customer
	accepted_notifications = Notification.objects.filter(
		Q(message__icontains="accepted")|Q(message__icontains="suggested")|Q(message__icontains="completed"),
		recipient=request.user).order_by('-created_date')
	context = {"notifications": accepted_notifications}
	return render(request,"customer/allnotificationscustomer.html",context)


@login_required
def suggest_price_to_customer(request,booking_id): #tasker suggesting price to customer

	booking = get_object_or_404(Booking, id=booking_id)

	if booking.confirmed_price is not None:
		messages.warning(request, "You have already suggested a price for this booking.")

		return redirect("all_notifications")

	if request.method=="POST":
		

		suggest_price=request.POST.get('suggest_price')
		print("suggest_price",suggest_price)

		if suggest_price:
			
			booking.confirmed_price=suggest_price
			booking.save()
			Notification.objects.create(
				recipient=booking.customer.user,
				message=f"Your tasker has suggested a new price of {booking.confirmed_price}.",
				booking=booking 
			)
			messages.success(request, "Price suggestion sent to the customer.")
			return redirect('all-notifications')  # Adjust redirect as needed
		else:
			messages.error(request, "Please enter a valid price.")


	return redirect('all-notifications')


@login_required
def accept_suggested_price(request,booking_id): #customer accepting the suggestprice from tasker
	booking = get_object_or_404(Booking,id=booking_id,customer_user=request.user)

	if booking.confirmed_price is not None:
		messages.warning(request, "No suggested price to accept.")
		return redirect("cust_notification_all")

	if request.method=="POST":
		booking.price_accepted=True
		booking.save()

		Notification.objects.create(
			recipient=booking.tasker.user,
			message=f"The customer has accepted your suggested price of {booking.confirmed_price}.",
			booking=booking 
		)

		messages.success(request, "You have accepted the suggested price.")
		return redirect("cust_notification_all")

	return redirect("cust_notification_all")


# this views for to see tasker profile,profile feed,activity   for customer


@login_required
def taskprofile(request, tasker_id):
    tasker = get_object_or_404(TaskerProfile, id=tasker_id)  # Fetch the specific tasker
    all_taskers = TaskerProfile.objects.all()  # Fetch all taskers
    today = date.today()
    tomorrow = today + timedelta(days=1)
    now = timezone.localtime().time()
     
 
    # Get bookings for today and tomorrow with 'accept' status
    bookings = Booking.objects.filter(
        tasker=tasker,
        date_booking__in=[today, tomorrow],
        status__iexact='accept'
    ).order_by('start_time')

    feed_items = []
    for booking in bookings:
        print(f"📖 Booking: {booking.customer.user.username} - {booking.service.name} | {booking.date_booking} | {booking.start_time} to {booking.end_time}", flush=True)

        if booking.date_booking == today:
            if booking.start_time <= now <= booking.end_time:
                status = "In Work"
            elif now < booking.start_time:
                status = "Pending"
            else:
                status = "Completed"
        else:
            status = "Upcoming"

        feed_items.append({'booking': booking, 'status': status})
    
 # ✅ NEW: Dynamically fetch completed tasks (before today or earlier today)
    completed_tasks = Booking.objects.filter(
        tasker=tasker,
        status__iexact='accept'
    ).filter(
        date_booking__lt=today
    ) | Booking.objects.filter(
        tasker=tasker,
        status__iexact='accept',
        date_booking=today,
        end_time__lt=now
    )

    # ✅ NEW: Order completed tasks latest first
    completed_tasks = completed_tasks.order_by('-date_booking', '-end_time')

    # ✅ Fetch reviews for this tasker
    reviews = Review.objects.filter(tasker=tasker).order_by('-created_at')

    context = {
        'tasker': tasker,
        'feed_items': feed_items,
        'all_taskers': all_taskers,
        'completed_tasks': completed_tasks,
		'reviews': reviews,
		
    }

    return render(request, 'customer/takser_profile_cust_view.html', context)




# this view for the customer profile seen by customer 


# @login_required
# def customer_profile_view(request):
#     customer = get_object_or_404(CustomerProfile, user=request.user)

#     # Recent bookings by customer
#     recent_bookings = Booking.objects.filter(
#         customer=customer
#     ).order_by('-date_booking')[:10]

#     # Payment history for the customer
#     payments = Payment.objects.filter(
#         customer=customer
#     ).order_by('-timestamp')[:10]

#     # Reviews made by the customer
#     reviews = Review.objects.filter(
#         customer=customer
#     ).order_by('-created_at')

#     # You can dynamically assign statuses for template display if needed
#     booking_list = []
#     for booking in recent_bookings:
#         if booking.status.lower() == 'completed':
#             status_display = 'Completed'
#         elif booking.status.lower() == 'accept':
#             status_display = 'Pending'
#         else:
#             status_display = booking.status.capitalize()

#         booking_list.append({
#             'booking': booking,
#             'status': status_display
#         })

#     context = {
#         'customer': customer,
#         'recent_bookings': booking_list,
#         'payments': payments,
#         'reviews': reviews,
#     }

#     return render(request, 'customer/profilecustomer.html', context)





# Adding review functions from customer to tasker 


@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer__user=request.user)

    if request.method == "POST":
        rating = request.POST.get("rating")
        review_msg = request.POST.get("custom_review") or request.POST.get("review_message")

        if rating and review_msg:
            if not hasattr(booking, 'review'):   # Prevent duplicate reviews
                customer_profile = CustomerProfile.objects.get(user=request.user)
                tasker_profile = booking.tasker  # Already a TaskerProfile instance

                Review.objects.create(
                    booking=booking,
                    customer=customer_profile,
                    tasker=tasker_profile,
                    rating=int(rating),
                    message=review_msg
                )
                messages.success(request, "Thank you for your review!")
            else:
                messages.warning(request, "You have already reviewed this task.")
        else:
            messages.error(request, "Please fill in both rating and review.")

    return redirect('cust_all_notifications')




