from .models import Users
from django.contrib.auth import logout, authenticate
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        login = request.POST['login']
        password = request.POST['password']
        try:
            user = Users.objects.get(login=login)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                request.session['username'] = user.login  # Сохраняем имя пользователя в сессии
                return redirect('main')
            else:
                messages.error(request, 'Неверный логин или пароль')
        except Users.DoesNotExist:
            messages.error(request, 'Пользователь не найден')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')