from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .models import GroupRoom, DirectRoom, Message
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.
def Chathome_view(request):
    user = request.user
    groups= GroupRoom.objects.filter(is_deleted=False)
    directs = DirectRoom.objects.all()
    for direct in directs:
        direct.other_user = direct.user2 if direct.user1 == user else direct.user1
    return render(request, 'room/chatroom.html', {'user': user, 'groups': groups, 'directs': directs})


def create_group_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        user = request.user
        is_private = request.POST.get('is_private') == 'on'
        password = request.POST.get('password') if is_private else ''

        if not name:
            messages.error(request, 'Room name is required.')
            return redirect('chat-home')

        if GroupRoom.objects.filter(name__iexact=name).exists():
            messages.error(request, f"A room named '{name}' already exists. Please choose a different name.")
            return redirect('chat-home')


        room = GroupRoom.objects.create(
            name=name,
            owner=user,
            room_type='private' if is_private else 'public',
            password=password
        )
        room.members.add(user)
        messages.success(request, 'Group room created successfully.')
        return redirect('chat-home')

    return render(request, 'room/create_group.html')


def join_group_room(request, slug):
    room = get_object_or_404(GroupRoom, slug=slug, is_deleted=False)
    if request.method == 'POST':
        password = request.POST.get('password')
        if room.password and room.password != password:
            messages.error(request, 'Incorrect password.')
            return redirect('chat-home')
        room.members.add(request.user)
        messages.success(request, f'You have joined the group: {room.name}')
        return redirect('chat-home')
    return render(request, 'room/join_group.html', {'room': room})

def leave_group_room(request, slug):
    room = get_object_or_404(GroupRoom, slug=slug, is_deleted=False)
    
    if request.method == 'POST':
        if room.owner == request.user:
            messages.error(request, 'You cannot leave a room you own. Please delete the room instead.')
            return redirect('chat-home')

        room.members.remove(request.user)
        messages.success(request, f'You have left the group: {room.name}')
        return redirect('chat-home')

    return render(request, 'room/leave_group.html', {'room': room})


def delete_group_room(request, slug):
    room = get_object_or_404(GroupRoom, slug=slug, is_deleted=False)
    if request.method == 'POST':
        if room.owner != request.user:
            messages.error(request, 'You do not have permission to delete this room.')
            return redirect('chat-home')
        room.is_deleted = True
        room.save()
        messages.success(request, f'Group room {room.name} has been deleted.')
        return redirect('chat-home')
    return render(request, 'room/delete_group.html', {'room': room})


def group_room_detail(request, slug):
    room = get_object_or_404(GroupRoom, slug=slug, is_deleted=False)
    room_ct = ContentType.objects.get_for_model(GroupRoom)
    is_member = request.user == room.owner or room.members.filter(id=request.user.id).exists()

    if not is_member:
        messages.warning(request, "You must join the group to view and send messages.")
        return redirect('chat-home')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=request.user,
                content=content,
                content_type=room_ct,
                object_id=room.id
            )
            messages.success(request, "Message sent successfully.")
        else:
            messages.error(request, "Message cannot be empty.")
        return redirect('group_room_detail', slug=room.slug)

    messages_list = Message.objects.filter(
        content_type=room_ct,
        object_id=room.id
    )

    return render(request, 'room/group_chat.html', {
        'room': room,
        'chat_messages': messages_list,
        'is_member': is_member,
    })



def direct_room_detail(request, room_id):
    room = get_object_or_404(DirectRoom, id=room_id)
    user = request.user

    if user not in [room.user1, room.user2]:
        messages.error(request, "You do not have permission to view this chat.")
        return redirect('chat-home')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=user,
                content=content,
                content_type=ContentType.objects.get_for_model(DirectRoom),
                object_id=room.id
            )
            messages.success(request, "Message sent successfully.")
        else:
            messages.error(request, "Message cannot be empty.")
        return redirect('direct_room_detail', room_id=room.id)

    messages_list = Message.objects.filter(
        content_type=ContentType.objects.get_for_model(DirectRoom),
        object_id=room.id
    )

    return render(request, 'room/direct_chat.html', {
        'room': room,
        'chat_messages': messages_list,
    })
    
    
def create_direct_room(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    user = request.user

    if user == other_user:
        messages.error(request, "You cannot create a chat with yourself.")
        return redirect('chat-home')

    room, created = DirectRoom.objects.get_or_create(
        user1=user,
        user2=other_user
    )

    if created:
        messages.success(request, f"Direct chat created with {other_user.username}.")
    else:
        messages.info(request, f"You already have a chat with {other_user.username}.")

    return redirect('direct_room_detail', room_id=room.id)