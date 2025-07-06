from django.urls import path
from . import views

urlpatterns = [
    # Basic
    path('', views.chat, name='chat'),
]