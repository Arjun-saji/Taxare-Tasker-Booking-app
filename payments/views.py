from django.shortcuts import render
import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from .models import Payment
from taskservices.models import Booking
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import hmac
import hashlib

def create_payment(request, booking_id):  #this view is created for the payment creation 
    booking = get_object_or_404(Booking, id=booking_id)
    amount = int(booking.tasker_price_suggestion * 100)  # Razorpay accepts in paise

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})

    payment = Payment.objects.create(
        customer=booking.customer,
        booking=booking,
        amount=booking.tasker_price_suggestion,
        razorpay_order_id=order['id']
    )

    return render(request, 'payments/payment_checkout.html', {
        'payment': payment,
        'order_id': order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'booking': booking,
    })




@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = request.POST
        try:
            payment = Payment.objects.get(razorpay_order_id=data['razorpay_order_id'])
        except Payment.DoesNotExist:
            return HttpResponseBadRequest()

        # Verify signature
        generated_signature = hmac.new(
            key=bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
            msg=bytes(data['razorpay_order_id'] + "|" + data['razorpay_payment_id'], 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        if generated_signature == data['razorpay_signature']:
            payment.paid = True
            payment.razorpay_payment_id = data['razorpay_payment_id']
            payment.razorpay_signature = data['razorpay_signature']
            payment.save()
            return render(request, 'payments/payment_success.html', {'payment': payment})

        return HttpResponseBadRequest("Invalid signature")


