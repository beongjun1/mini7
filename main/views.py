from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
        

def main_view(request):
    return render(request, 'main.html')


def greet(request):
    return render(request, 'greet.html')

def qa(request):
    return render(request, 'qa.html')

def program(request):
    return render(request, 'program.html')

    


    

 