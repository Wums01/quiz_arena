from django.urls import re_path

websocket_urlpatterns = [
    re_path(r"ws/room/(?P<room_code>\w+)/$", "game.consumers.RoomConsumer"),
]