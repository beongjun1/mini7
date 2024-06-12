
from django.urls import path, include
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.main_view),
    path('chatgpt/',include('chatgpt.urls')),
]