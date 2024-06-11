from django.db import models

# class Chat(models.Model):
#     query = models.CharField(max_length=255)
#     answer = models.CharField(max_length=255)
#     datetime = models.DateTimeField(auto_now_add=True)
#     sim1 = models.FloatField()
#     sim2 = models.FloatField()
#     sim3 = models.FloatField()

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    
class Message(models.Model):
    user = models.CharField(max_length=255)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}: {self.text[:50]}"