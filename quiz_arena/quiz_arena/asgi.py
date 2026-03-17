import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quiz_arena.settings")

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from game.consumers import RoomConsumer  # import AFTER Django setup

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/room/<str:room_code>/", RoomConsumer.as_asgi()),
        ])
    ),
})