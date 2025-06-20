import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.contenttypes.models import ContentType
from .models import Message, GroupRoom, DirectRoom

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = f"group_{self.slug}"

        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if 'typing' in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': self.scope["user"].username,
                    'is_typing': data['typing']
                }
            )
            return
            
        message = data['message']
        user = self.scope["user"]

        group_room = await self.get_group(self.slug)
        if not group_room:
            return

        await self.save_message(user, message, group_room)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
        }))

    async def typing_indicator(self, event):
    # Don't send typing notification back to the sender
        if event['username'] != self.scope["user"].username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    @database_sync_to_async
    def get_group(self, slug):
        try:
            return GroupRoom.objects.get(slug=slug, is_deleted=False)
        except GroupRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, user, message, group_room):
        content_type = ContentType.objects.get_for_model(GroupRoom)
        return Message.objects.create(
            sender=user,
            content=message,
            content_type=content_type,
            object_id=group_room.id
        )

class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"direct_{self.room_id}"

        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if 'typing' in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': self.scope["user"].username,
                    'is_typing': data['typing']
                }
            )
            return
            
        message = data['message']
        user = self.scope["user"]

        direct_room = await self.get_direct(self.room_id)
        if not direct_room:
            return

        await self.save_message(user, message, direct_room)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def get_direct(self, room_id):
        try:
            return DirectRoom.objects.get(id=room_id)
        except DirectRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, user, message, direct_room):
        content_type = ContentType.objects.get_for_model(DirectRoom)
        return Message.objects.create(
            sender=user,
            content=message,
            content_type=content_type,
            object_id=direct_room.id
        )