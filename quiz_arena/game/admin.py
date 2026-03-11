from django.contrib import admin
from .models import Question, Result, GameRoom, MultiplayerPlayer, PlayerAnswer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "category", "difficulty", "correct_option")
    list_filter = ("category", "difficulty")
    search_fields = ("text",)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("player_name", "score", "total_questions", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("player_name",)


@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ("room_code", "host_name", "category", "current_question", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("room_code", "host_name")


@admin.register(MultiplayerPlayer)
class MultiplayerPlayerAdmin(admin.ModelAdmin):
    list_display = ("player_name", "room", "score", "joined_at")
    list_filter = ("room", "joined_at")
    search_fields = ("player_name", "room__room_code")


@admin.register(PlayerAnswer)
class PlayerAnswerAdmin(admin.ModelAdmin):
    list_display = ("player", "room", "question", "selected_option", "is_correct", "answered_at")
    list_filter = ("is_correct", "room", "answered_at")
    search_fields = ("player__player_name", "room__room_code", "question__text")