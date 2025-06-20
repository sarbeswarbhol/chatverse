from django.contrib import admin
from .models import GroupRoom, DirectRoom, Message


@admin.register(GroupRoom)
class GroupRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'owner', 'created_at', 'is_deleted')
    list_filter = ('room_type', 'is_deleted')
    search_fields = ('name', 'description', 'owner__username')


@admin.register(DirectRoom)
class DirectRoomAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('get_room_display', 'sender', 'content', 'created_at')
    list_filter = ('created_at', 'is_deleted')
    search_fields = ('content', 'sender__username')

    def get_room_display(self, obj):
        return f"{obj.room}"
    get_room_display.short_description = 'Room'
