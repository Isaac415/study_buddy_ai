from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse

# Create your views here.

# homepage after logged in
def home(request):
    return HttpResponse(f"<h1>Hi, {request.user}!</h1>")

# login
def login(request):
    return 

# register
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

# logout