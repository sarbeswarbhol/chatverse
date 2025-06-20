from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Chathome_view, name='chat-home'),
    path('create-group/', views.create_group_room, name='create_group_room'),
    path('delete-group/<slug:slug>/', views.delete_group_room, name='delete_group_room'),
    path('join-group/<slug:slug>/', views.join_group_room, name='join_group_room'),
    path('leave-group/<slug:slug>/', views.leave_group_room, name='leave_group_room'),
    path('group/<slug:slug>/', views.group_room_detail, name='group_room_detail'),
    path('direct/<uuid:room_id>/', views.direct_room_detail, name='direct_room_detail'),
    path('direct/create/<int:user_id>/', views.create_direct_room, name='create_direct_room'),
]