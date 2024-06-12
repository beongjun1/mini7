from django.db import models

# class Chat(models.Model):
#     query = models.CharField(max_length=255)
#     answer = models.CharField(max_length=255)
#     datetime = models.DateTimeField(auto_now_add=True)
#     sim1 = models.FloatField()
#     sim2 = models.FloatField()
#     sim3 = models.FloatField()

class Chat(models.Model):
    # 썸네일 - 새로운 방id 생길때 최초 유저 메세지 앞 10글자
    thumbnail = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.thumbnail

class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255, default='1')
    user = models.CharField(max_length=255)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}: {self.text[:50]}"
    
class EmbeddingFulltextSearchContent(models.Model):
    id = models.IntegerField(primary_key=True)
    c0 = models.TextField()
    string_value = models.TextField(null=True)


class QA(models.Model):
    category = models.CharField(max_length=100)
    qa = models.TextField()
