from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course

# Create your views here.

'''
Basic
'''

# Landing page
def home(request):
    return render(request, 'landing.html')

# Homepage after logged in
@login_required
def dashboard(request):
    context = {
        "user": request.user
    }
    return render(request, 'dashboard.html', context)


'''
Authentication
'''
# Login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/dashboard')
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
                return redirect('/dashboard')
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

'''
Course
'''
@login_required
def course(request):
    courses = Course.objects.filter(user=request.user)
    context = {
        'courses': courses
    }
    return render(request, 'course.html', context)

def create_course(request):
    if request.method == 'POST':
        name = request.POST['name'].strip()
        description = request.POST['description'].strip()
        color = request.POST['color']

        # Create course and save to database
        course = Course(name=name,
                        description=description,
                        user=request.user,
                        color=color,
                        )
        course.save()

        return redirect('/course')

'''
Document
'''
