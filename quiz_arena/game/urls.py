from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('start/', views.start_game, name='start'),
    path('question/', views.question_view, name='question'),
    path('result/', views.result_view, name='result'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),

    path('multiplayer/', views.multiplayer_home, name='multiplayer'),
    path('multiplayer/create/', views.create_room, name='create_room'),
    path('multiplayer/join/', views.join_room, name='join_room'),
    path('multiplayer/room/<str:room_code>/', views.room_lobby, name='room_lobby'),

    path('multiplayer/game/<str:room_code>/', views.multiplayer_game, name='multiplayer_game'),
    path('multiplayer/game/<str:room_code>/answer/', views.submit_multiplayer_answer, name='submit_multiplayer_answer'),
    path('multiplayer/game/<str:room_code>/next/', views.next_multiplayer_question, name='next_multiplayer_question'),
    path('multiplayer/stats/<str:room_code>/', views.multiplayer_stats, name='multiplayer_stats'),
    path(
    'multiplayer/round-leaderboard/<str:room_code>/',
    views.multiplayer_round_leaderboard,
    name='multiplayer_round_leaderboard'),
    path('multiplayer/result/<str:room_code>/', views.multiplayer_result, name='multiplayer_result'),
    path('multiplayer/start/<str:room_code>/', views.start_multiplayer_game, name='start_multiplayer_game'),
]