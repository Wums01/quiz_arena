from django.db import models


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('Bible', 'Bible'),
        ('General', 'General'),
        ('Music', 'Music'),
        ('Nigeria', 'Nigeria'),
        ('World', 'World'),
        ('Sport', 'Sport'),
        ('The Elevation Church', 'The Elevation Church'),
    ]

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    text = models.CharField(max_length=255)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)

    def __str__(self):
        return self.text


class Result(models.Model):
    player_name = models.CharField(max_length=100)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    category = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_name} - {self.score}/{self.total_questions}"


class GameRoom(models.Model):
    room_code = models.CharField(max_length=8, unique=True)
    host_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    current_question = models.IntegerField(default=0)
    is_started = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_code


class MultiplayerPlayer(models.Model):
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name="players")
    player_name = models.CharField(max_length=100)
    score = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'player_name')

    def __str__(self):
        return f"{self.player_name} - {self.room.room_code} - Score: {self.score}"


class PlayerAnswer(models.Model):
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    player = models.ForeignKey(MultiplayerPlayer, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.IntegerField()
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'player', 'question')

    def __str__(self):
        return f"{self.player.player_name} - {self.question.text[:20]}"