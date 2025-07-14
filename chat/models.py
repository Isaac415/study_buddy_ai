from django.db import models
from nanoid import generate

# Create your models here.
class Chat(models.Model):
    id = models.CharField(primary_key=True, default=generate, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=True, blank=True)
    last_message_time = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

class Message(models.Model):
    ROLE_OPTIONS = [
        ('system','system'),
        ('human', 'human'),
        ('ai', 'ai'),
        ('tool', 'tool'),
    ]

    id = models.CharField(primary_key=True, default=generate, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_OPTIONS, default="human")
    content = models.CharField(max_length=1000, null=True, blank=True)
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content