from . import views
from django.urls import path ,include
from .views import mark_notification_as_read



urlpatterns=[path('services/filter/<int:service_id>/', views.taskfilter_view, name='filters'),
 path('book/<int:tasker_id>/<int:service_id>/', views.book_service, name='book_service'),
 path('cusomerprofile/', views.profile_customer, name='customer_view'),
 path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
 path('booking/<int:booking_id>/accept/', views.accept_booking_tasker, name='accept_booking'),
 path('all-notifications/', views.cust_notification_all, name='cust_all_notifications'),
 path('suggest-price/<int:booking_id>/', views.suggest_price_to_customer, name='suggest_price'),
 path('accept-suggested-price/<int:booking_id>/', views.accept_suggested_price, name='accept_suggested_price'),
 path('taskerprofiles/<int:tasker_id>/', views.taskprofile, name='tasker_profiles'),
 path('add-review/<int:booking_id>/', views.add_review, name='add_review'),
#  path('customer/profile/', views.customer_profile_view, name='customer_profile_view'),


]

