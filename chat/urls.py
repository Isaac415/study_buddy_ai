from django.urls import path
from . import views

urlpatterns = [
    # Basic
    path('', views.chat, name='chat'),
    path('/create', views.create_chat, name='create_chat'),
    path('/<slug:chat_id>', views.chatroom, name='chatroom'),
]