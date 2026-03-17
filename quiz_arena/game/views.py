from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import (
    Question,
    Result,
    GameRoom,
    MultiplayerPlayer,
    PlayerAnswer,
)
import random
import string



def get_category_timer(category):
    timers = {
        "Bible": 12,
        "General": 10,
        "Music": 8,
        "Nigeria": 10,
        "World": 10,
        "Sport": 8,
        "The Elevation Church": 12,
    }
    return timers.get(category, 10)


def home(request):
    return render(request, "home.html")


# ---------------- SOLO MODE ----------------

def start_game(request):
    categories = Question.objects.values_list('category', flat=True).distinct()

    if request.method == "POST":
        name = request.POST.get("player_name")
        category = request.POST.get("category")

        questions = list(Question.objects.filter(category=category))
        random.shuffle(questions)
        questions = questions[:20]

        request.session["player_name"] = name
        request.session["category"] = category
        request.session["questions"] = [q.id for q in questions]
        request.session["score"] = 0
        request.session["index"] = 0
        request.session["result_saved"] = False

        return redirect("question")

    return render(request, "start.html", {
        "categories": categories
    })

def question_view(request):
    index = request.session.get("index", 0)
    questions = request.session.get("questions", [])
    player_name = request.session.get("player_name", "Player")
    category = request.session.get("category", "Quiz")

    if not questions:
        return redirect("start")

    if index >= len(questions):
        return redirect("result")

    question = Question.objects.get(id=questions[index])

    if request.method == "POST":
        selected = request.POST.get("answer")

        if selected and int(selected) == question.correct_option:
            request.session["score"] = request.session.get("score", 0) + 1

        request.session["index"] = index + 1
        return redirect("question")

    return render(request, "question.html", {
        "question": question,
        "current": index + 1,
        "total": len(questions),
        "player_name": player_name,
        "category": category,
        "question_timer": get_category_timer(category),
    })

def result_view(request):
    score = request.session.get("score", 0)
    total = len(request.session.get("questions", []))
    player_name = request.session.get("player_name", "Player")
    category = request.session.get("category", "Quiz")
    result_saved = request.session.get("result_saved", False)

    if total > 0 and not result_saved:
        Result.objects.create(
            player_name=player_name,
            score=score,
            total_questions=total,
            category=category,
            difficulty="Mixed"
        )
        request.session["result_saved"] = True

    all_results = list(Result.objects.order_by("-score", "created_at"))
    rank = None

    for index, result in enumerate(all_results, start=1):
        if (
            result.player_name == player_name
            and result.score == score
            and result.category == category
        ):
            rank = index
            break

    return render(request, "result.html", {
        "score": score,
        "total": total,
        "player_name": player_name,
        "category": category,
        "rank": rank,
    })


def leaderboard_view(request):
    results = Result.objects.order_by("-score", "created_at")[:10]
    total_players = Result.objects.values("player_name").distinct().count()
    return render(request, "leaderboard.html", {
        "results": results
    })


# ---------------- MULTIPLAYER MODE ----------------

def multiplayer_home(request):
    return render(request, "multiplayer_home.html")


def create_room(request):
    if request.method == "POST":
        host_name = request.POST.get("host_name")
        category = request.POST.get("category")

        room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        while GameRoom.objects.filter(room_code=room_code).exists():
            room_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        room = GameRoom.objects.create(
            room_code=room_code,
            host_name=host_name,
            category=category,
            current_question=0
        )

        request.session["player_name"] = host_name

        MultiplayerPlayer.objects.get_or_create(
            room=room,
            player_name=host_name
        )

        return redirect("room_lobby", room_code=room.room_code)

    categories = Question.objects.values_list('category', flat=True).distinct()
    return render(request, "create_room.html", {"categories": categories})


def join_room(request):
    error = None

    if request.method == "POST":
        player_name = request.POST.get("player_name")
        room_code = request.POST.get("room_code", "").upper()

        room = GameRoom.objects.filter(room_code=room_code).first()

        if room:
            request.session["player_name"] = player_name

            MultiplayerPlayer.objects.get_or_create(
                room=room,
                player_name=player_name
            )

            return redirect("room_lobby", room_code=room.room_code)
        else:
            error = "Room not found. Check the code and try again."

    return render(request, "join_room.html", {"error": error})


def room_lobby(request, room_code):
    room = GameRoom.objects.get(room_code=room_code)
    if room.is_started:
       return redirect("multiplayer_game", room_code=room.room_code)
    player_name = request.session.get("player_name", room.host_name)
    is_host = player_name == room.host_name
    players = MultiplayerPlayer.objects.filter(room=room).order_by("joined_at")
    player_count = players.count()

    return render(request, "room_lobby.html", {
        "room": room,
        "player_name": player_name,
        "is_host": is_host,
        "players": players,
        "player_count": player_count,
    })


def multiplayer_game(request, room_code):
    room = GameRoom.objects.get(room_code=room_code)
    questions = list(Question.objects.filter(category=room.category))
    random.shuffle(questions)
    questions = questions[:20]

    player_name = request.session.get("player_name")
    is_host = player_name == room.host_name

    if not questions:
        return render(request, "multiplayer_question.html", {
            "room": room,
            "question": None,
            "current_number": 0,
            "total_questions": 0,
            "is_host": is_host,
            "player_score": 0,
            "players": [],
            "question_timer": get_category_timer(room.category),
        })

    total_questions = len(questions)

    if room.current_question >= total_questions:
        return redirect("multiplayer_result", room_code=room.room_code)

    question = questions[room.current_question]

    player = MultiplayerPlayer.objects.filter(
        room=room,
        player_name=player_name
    ).first()

    player_score = player.score if player else 0
    players = MultiplayerPlayer.objects.filter(room=room).order_by("-score", "player_name")

    return render(request, "multiplayer_question.html", {
        "room": room,
        "question": question,
        "current_number": room.current_question + 1,
        "total_questions": total_questions,
        "is_host": is_host,
        "player_score": player_score,
        "players": players,
        "question_timer": get_category_timer(room.category),
    })


def start_multiplayer_game(request, room_code):
    room = GameRoom.objects.get(room_code=room_code)

    player_name = request.session.get("player_name")
    if player_name != room.host_name:
        return JsonResponse({"error": "Only host can start the game"}, status=403)

    room.is_started = True
    room.save()

    return JsonResponse({"success": True})

    
def submit_multiplayer_answer(request, room_code):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    room = GameRoom.objects.get(room_code=room_code)
    player_name = request.session.get("player_name")

    if not player_name:
        return JsonResponse({"error": "Player not found in session"}, status=400)

    player = MultiplayerPlayer.objects.filter(room=room, player_name=player_name).first()
    if not player:
        return JsonResponse({"error": "Player not found in room"}, status=404)

    questions = list(Question.objects.filter(category=room.category)[:20])
    if not questions:
        return JsonResponse({"error": "No questions found"}, status=404)

    current_index = room.current_question
    if current_index >= len(questions):
        current_index = len(questions) - 1

    question = questions[current_index]

    existing_answer = PlayerAnswer.objects.filter(
        room=room,
        player=player,
        question=question
    ).first()

    players = MultiplayerPlayer.objects.filter(room=room).order_by("-score", "player_name")
    leaderboard = [
        {"name": p.player_name, "score": p.score}
        for p in players
    ]

    if existing_answer:
        return JsonResponse({
            "success": False,
            "message": "You already answered this question.",
            "correct_option": question.correct_option,
            "score": player.score,
            "players": leaderboard
        })

    selected_option = request.POST.get("selected_option")
    if not selected_option:
        return JsonResponse({"error": "No answer selected"}, status=400)

    selected_option = int(selected_option)
    is_correct = selected_option == question.correct_option

    PlayerAnswer.objects.create(
        room=room,
        player=player,
        question=question,
        selected_option=selected_option,
        is_correct=is_correct
    )

    if is_correct:
        player.score += 1
        player.save()

    players = MultiplayerPlayer.objects.filter(room=room).order_by("-score", "player_name")
    leaderboard = [
        {"name": p.player_name, "score": p.score}
        for p in players
    ]

    return JsonResponse({
        "success": True,
        "correct": is_correct,
        "correct_option": question.correct_option,
        "score": player.score,
        "players": leaderboard
    })


def multiplayer_stats(request, room_code):
    room = GameRoom.objects.get(room_code=room_code)

    questions = list(Question.objects.filter(category=room.category)[:20])
    total_questions = len(questions)

    if total_questions == 0:
        return redirect("multiplayer_game", room_code=room_code)

    current_index = room.current_question

    if current_index >= total_questions:
        current_index = total_questions - 1

    question = questions[current_index]
    answers = PlayerAnswer.objects.filter(room=room, question=question)

    option1_count = answers.filter(selected_option=1).count()
    option2_count = answers.filter(selected_option=2).count()
    option3_count = answers.filter(selected_option=3).count()
    option4_count = answers.filter(selected_option=4).count()

    correct_count = answers.filter(is_correct=True).count()
    wrong_count = answers.filter(is_correct=False).count()

    players = MultiplayerPlayer.objects.filter(room=room).order_by("-score", "player_name")

    return render(request, "multiplayer_stats.html", {
        "room": room,
        "question": question,
        "current_number": current_index + 1,
        "total_questions": total_questions,
        "option1_count": option1_count,
        "option2_count": option2_count,
        "option3_count": option3_count,
        "option4_count": option4_count,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "players": players,
        "is_host": request.session.get("player_name") == room.host_name,
    })


def next_multiplayer_question(request, room_code):
    room = GameRoom.objects.get(room_code=room_code)

    player_name = request.session.get("player_name")
    if player_name != room.host_name:
        return JsonResponse({"error": "Only host can move to next question"}, status=403)

    total_questions = Question.objects.filter(category=room.category)[:20].count()

    if room.current_question < total_questions:
        room.current_question += 1
        room.save()

    game_finished = room.current_question >= total_questions

    return JsonResponse({
        "success": True,
        "current_question": room.current_question,
        "game_finished": game_finished
    })


def multiplayer_round_leaderboard(request, room_code):
    room = GameRoom.objects.get(room_code=room_code)
    players = MultiplayerPlayer.objects.filter(room=room).order_by("-score", "player_name")

    total_questions = Question.objects.filter(category=room.category)[:20].count()
    current_number = room.current_question + 1

    if current_number > total_questions:
        current_number = total_questions

    return render(request, "multiplayer_round_leaderboard.html", {
        "room": room,
        "players": players,
        "current_number": current_number,
        "total_questions": total_questions,
        "is_host": request.session.get("player_name") == room.host_name,
    })


def multiplayer_result(request, room_code):
    room = GameRoom.objects.get(room_code=room_code)
    player_name = request.session.get("player_name")

    players = MultiplayerPlayer.objects.filter(room=room).order_by("-score", "player_name")
    my_player = players.filter(player_name=player_name).first()

    total_questions = Question.objects.filter(category=room.category)[:20].count()
    my_score = my_player.score if my_player else 0

    return render(request, "multiplayer_result.html", {
        "room": room,
        "players": players,
        "my_score": my_score,
        "total_questions": total_questions,
        "player_name": player_name,
    })