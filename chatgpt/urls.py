from django.urls import path
from . import views

app_name = 'chatgpt'
urlpatterns = [
    # path('', views.index, name='index'),
    # path('chat', views.chat, name='chat'),
    path('', views.chat_view, name='chat'),
    path('api/chat/', views.chat, name='chat_api'),
    path('add_room/', views.add_chat_room, name='chatgpt:add_chat_room'),
    path('download/', views.download, name='download_chat_history'),
  
]
