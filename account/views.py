from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.db.utils import IntegrityError
from django.contrib.auth import login

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        phone_number = request.POST['phone-number']
        address = request.POST['address']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/signup.html')
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            Profile.objects.create(user=user, phone_number=phone_number, address=address)
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        except IntegrityError:
            messages.error(request, 'Username or email already exists.')
            return render(request, 'registration/signup.html')

    return render(request, 'registration/signup.html')


class MyPasswordChangeView(PasswordChangeView) :
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.info(self.request, '암호 변경을 완료했습니다!')
        return super().form_valid(form)