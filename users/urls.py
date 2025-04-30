from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
from .views import notification_all
from .views import servicespage


urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path("tasker/register/",task_register,name='task_register'),
    path("customer/register/",customer_register,name='customer_register'),
    path("logout/",logout_view,name='logout_view'),
    path('customer_login/', customerlogin_view, name='customerlogin_view'),
    path('tasker_login/', taskerlogin_view, name='taskerlogin_view'),
    path('tasker_profile/<int:user_id>/',tasker_profile,name='tasker_profile'),
    path('customer_profile/<int:user_id>/',customer_profile,name='customer_profile'),
    path("single/<int:object_id>/",singlecust,name="singlecust"),
    path('tasker/profile/',tasker_profile_view, name='taskerprofile'),  # for logged-in tasker
    path('tasker/<int:tasker_id>/profile/', tasker_profile_view),    
    path('all-notifications/', notification_all, name='all_notifications'),
    path('landing/', landingcustomer, name='landing'),
    path('', home, name='home'),
    path('services/',servicespage,name='services'),
    path('aboutus/',aboutspage,name='aboutus'),
    path('contactus/',contacus,name='contactus'),
]   