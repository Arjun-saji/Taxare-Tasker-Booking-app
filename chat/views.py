from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q 
from .models import ChatMessage
User = get_user_model()




@login_required
def chat_room(request, room_name, receiver_username):
    sender_user = request.user
    receiver_user = get_object_or_404(User, username=receiver_username)

    # Fetch chat messages between the sender and receiver
    # messages = ChatMessage.objects.filter(
    #     Q(sender=sender_user, receiver=receiver_user) |
    #     Q(sender=receiver_user, receiver=sender_user)
    # ).order_by('timestamp')

    messages = ChatMessage.objects.filter(
    Q(sender=sender_user, receiver=receiver_user) |
    Q(sender=receiver_user, receiver=sender_user)
    ).order_by('timestamp')


    return render(request, 'chat/chat_room.html', {
        'room_name': room_name,
        'sender': sender_user.username,
        'receiver': receiver_user.username,
        'messages': messages
    })

