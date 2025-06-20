
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/group/(?P<slug>[^/]+)/$', consumers.GroupChatConsumer.as_asgi()),
    re_path(r'ws/chat/direct/(?P<room_id>[^/]+)/$', consumers.DirectChatConsumer.as_asgi()),
]
