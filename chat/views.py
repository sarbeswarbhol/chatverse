from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from .models import GroupRoom, DirectRoom, Message

# Home View
def Chathome_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    groups = GroupRoom.objects.filter(is_deleted=False)
    directs = DirectRoom.objects.filter(Q(user1=user) | Q(user2=user))

    for direct in directs:
        direct.other_user = direct.user2 if direct.user1 == user else direct.user1

    users = User.objects.exclude(id=user.id)

    return render(request, 'room/chatroom.html', {
        'user': user,
        'groups': groups,
        'directs': directs,
        'users': users,
    })


# Create Group Room
def create_group_room(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        is_private = request.POST.get('is_private') == 'on'
        password = request.POST.get('password', '').strip() if is_private else ''
        
        if not name:
            messages.error(request, 'Room name is required.')
            return redirect('chat-home')

        if GroupRoom.objects.filter(name__iexact=name).exists():
            messages.error(request, f"A room named '{name}' already exists.")
            return redirect('chat-home')

        room = GroupRoom.objects.create(
            name=name,
            owner=request.user,
            room_type='private' if is_private else 'public',
            password=password
        )
        room.members.add(request.user)
        messages.success(request, f"Group room '{name}' created successfully.")
        return redirect('chat-home')

    return render(request, 'room/create_group.html')


# Join Group Room
def join_group_room(request, slug):
    room = get_object_or_404(GroupRoom, slug=slug, is_deleted=False)
    
    if request.method == 'POST':
        password = request.POST.get('password', '').strip()

        if room.room_type == 'private' and room.password != password:
            messages.error(request, 'Incorrect password.')
            return redirect('chat-home')

        room.members.add(request.user)
        messages.success(request, f"You've joined the group: {room.name}")
        return redirect('group_room_detail', slug=slug)

    return render(request, 'room/join_group.html', {'room': room})


# Leave Group Room
def leave_group_room(request, slug):
    room = get_object_or_404(GroupRoom, slug=slug, is_deleted=False)

    if request.method == 'POST':
        if room.owner == request.user:
            messages.error(request, 'Owners cannot leave their own room. Delete it instead.')
            return redirect('chat-home')

        room.members.remove(request.user)
        messages.success(request, f"You left the group: {room.name}")
        return redirect('chat-home')

    return render(request, 'room/leave_group.html', {'room': room})


# Delete Group Room
def delete_group_room(request, slug):
    room = get_object_or_404(GroupRoom, slug=slug, is_deleted=False)

    if request.method == 'POST':
        if room.owner != request.user:
            messages.error(request, "You are not allowed to delete this room.")
            return redirect('chat-home')

        room.is_deleted = True
        room.save()
        messages.success(request, f"Group room '{room.name}' deleted successfully.")
        return redirect('chat-home')

    return render(request, 'room/delete_group.html', {'room': room})


# Group Chat View
def group_room_detail(request, slug):
    group_ct = ContentType.objects.get_for_model(GroupRoom)
    room = get_object_or_404(GroupRoom, slug=slug, is_deleted=False)
    is_member = room.owner == request.user or room.members.filter(id=request.user.id).exists()

    if not is_member:
        messages.warning(request, "You must join the group to view messages.")
        return redirect('chat-home')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=request.user,
                content=content,
                content_type=group_ct,
                object_id=room.id
            )
            messages.success(request, "Message sent.")
        else:
            messages.error(request, "Message cannot be empty.")
        return redirect('group_room_detail', slug=slug)

    messages_list = Message.objects.filter(content_type=group_ct, object_id=room.id).select_related('sender')

    return render(request, 'room/group_chat.html', {
        'room': room,
        'chat_messages': messages_list,
        'is_member': is_member,
    })


# Direct Chat View
def direct_room_detail(request, room_id):
    direct_ct = ContentType.objects.get_for_model(DirectRoom)
    room = get_object_or_404(DirectRoom, id=room_id)
    user = request.user

    if user not in [room.user1, room.user2]:
        messages.error(request, "You are not allowed to view this chat.")
        return redirect('chat-home')

    
    other_user = room.user2 if room.user1 == user else room.user1
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=user,
                content=content,
                content_type=direct_ct,
                object_id=room.id
            )
            messages.success(request, "Message sent.")
        else:
            messages.error(request, "Message cannot be empty.")
        return redirect('direct_room_detail', room_id=room.id)

    messages_list = Message.objects.filter(content_type=direct_ct, object_id=room.id).select_related('sender')

    return render(request, 'room/direct_chat.html', {
        'room': room,
        'other_user': other_user,
        'chat_messages': messages_list,
    })


# Create or Fetch Direct Chat Room
def create_direct_room(request, user_id):
    user = request.user
    other_user = get_object_or_404(User, id=user_id)

    if user == other_user:
        messages.error(request, "You cannot start a chat with yourself.")
        return redirect('chat-home')

    # Try both user combinations for existing chat
    room = DirectRoom.objects.filter(
        (Q(user1=user) & Q(user2=other_user)) | (Q(user1=other_user) & Q(user2=user))
    ).first()

    if room:
        messages.info(request, f"You already have a chat with {other_user.username}.")
    else:
        room = DirectRoom.objects.create(user1=user, user2=other_user)
        messages.success(request, f"Direct chat created with {other_user.username}.")

    return redirect('direct_room_detail', room_id=room.id)
