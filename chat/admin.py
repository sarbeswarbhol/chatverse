from django.contrib import admin
from .models import Room, Message 


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    list_filter = ('room_type', 'is_deleted')
    search_fields = ('name', 'owner__username', 'description')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'content', 'created_at')
    list_filter = ('room', 'created_at','is_deleted')
    search_fields = ('content',)