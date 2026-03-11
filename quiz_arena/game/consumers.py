import json
from channels.generic.websocket import AsyncWebsocketConsumer


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"room_{self.room_code}"

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
        message_type = data.get("type")

        if message_type == "start_game":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "game_started"}
            )

        elif message_type == "show_stats":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "stats_shown"}
            )

        elif message_type == "show_round_leaderboard":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "round_leaderboard_shown"}
            )

        elif message_type == "next_question":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "question_advanced"}
            )

        elif message_type == "finish_game":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "game_finished_event"}
            )

        elif message_type == "leaderboard_update":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "leaderboard_updated_event",
                    "players": data.get("players", [])
                }
            )

        elif message_type == "players_update":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "players_updated_event",
                    "players": data.get("players", [])
                }
            )

    async def game_started(self, event):
        await self.send(text_data=json.dumps({"type": "game_started"}))

    async def stats_shown(self, event):
        await self.send(text_data=json.dumps({"type": "stats_shown"}))

    async def round_leaderboard_shown(self, event):
        await self.send(text_data=json.dumps({"type": "round_leaderboard_shown"}))

    async def question_advanced(self, event):
        await self.send(text_data=json.dumps({"type": "question_advanced"}))

    async def game_finished_event(self, event):
        await self.send(text_data=json.dumps({"type": "game_finished"}))

    async def leaderboard_updated_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "leaderboard_updated",
            "players": event["players"]
        }))

    async def players_updated_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "players_updated",
            "players": event["players"]
        }))