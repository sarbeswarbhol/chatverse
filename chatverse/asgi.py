# chatverse/asgi.py
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack  # ✅ important
from django.core.asgi import get_asgi_application
import chat.routing  # ✅ your app's routing.py

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatverse.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # ✅ this is what gives you scope["user"]
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
