from django.urls import path
from . import views

urlpatterns = [
    # Basic
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),

    # Authentication
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # Course
    path('course', views.course, name='course'),
    path('course/create', views.create_course, name="create_course")
]