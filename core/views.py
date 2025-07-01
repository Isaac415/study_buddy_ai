from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

# Landing page
def landing(request):
    return HttpResponse(f'<h1 style="text-align:center;">Welcome to Study Buddy AI!</h1>')

# Homepage after logged in
@login_required
def home(request):
    return HttpResponse(f"<h1>Hi, {request.user}!</h1>")

# Login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/home')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

# Register
def register(request):
    # Register Form
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirmation = request.POST['password_confirmation']

        if password == password_confirmation:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                auth.login(request, user)
                return redirect('/home')
            except Exception as e:
                error_message = f'Error creating account: {str(e)}'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    
    # Load Page
    return render(request, 'register.html')

# Logout
def logout(request):
    auth.logout(request)
    return redirect('/')