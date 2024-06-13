from django.urls import path
from django.contrib import admin
from . import views

app_name = 'chatgpt'
urlpatterns = [
    path('', views.chat_view, name='chat_view'),
    path('chat_view/<int:chat_id>/', views.chat_view, name='chat_view'),
    path('api/chat/', views.chat, name='chat'),
    path('delete_chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('download/', views.download, name='download_chat_history'),
    path('admin/', admin.site.urls),
    path('api/session/', views.session_out, name='session_out'),
]
