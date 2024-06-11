# # blog/urls.py
# from django.urls import path
# from django.contrib import admin
# from . import views

# app_name = 'chatgpt'
# urlpatterns = [

#     path('', views.index, name='index'),
#     path('chat', views.chat, name='chat'),
#     path('get_previous_chats', views.get_previous_chats, name='get_previous_chats'),


# ]



from django.urls import path
from . import views

app_name = 'chatgpt'
urlpatterns = [
    # path('', views.index, name='index'),
    # path('chat', views.chat, name='chat'),
    path('', views.chat_view, name='chat'),
    path('api/chat/', views.chat, name='chat_api'),
]
