from django.urls import path
from . import views

urlpatterns = [
   
    path('<str:room_name>/<str:receiver_username>/', views.chat_room, name='chat_room'),
   
]
