from django.urls import path
from django.contrib import admin
from . import views

app_name = 'chatgpt'
urlpatterns = [
    path('', views.chat_view, name='chat_view'),
    path('chat_view/<int:chat_id>/', views.chat_view, name='chat_view'),
    path('api/chat/', views.chat, name='chat'),
    path('add_room/', views.add_chat_room, name='chatgpt:add_chat_room'),
    path('download/', views.download, name='download_chat_history'),
    path('admin/', admin.site.urls),
]
