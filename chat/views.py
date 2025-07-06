from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Chat
from core.models import Course
from django.contrib.auth.decorators import login_required
# Create your views here.

'''
Chat
'''
@login_required
def chat(request):
    chats = Chat.objects.filter(user=request.user)
    courses = Course.objects.filter(user=request.user)
    context = {
        'chats': chats,
        'courses': courses,
    }

    return render(request, 'chat.html', context)

@login_required
def create_chat(request):
    if request.method == "POST":
        chat = Chat(user=request.user)
        chat.save()

        chat_id = chat.id
        return redirect(f'/chat/{chat_id}')


from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage

load_dotenv()
llm = ChatDeepSeek(model="deepseek-chat")

@login_required
def chatroom(request, chat_id):
    # Handles chat message
    context = {
        'chat_id': chat_id,
    }

    if request.method == "POST":
        user_message = request.POST.get("message") + " DO NOT USE MARKDOWN!";
        response = llm.invoke([HumanMessage(content=user_message)])
        return JsonResponse({'response': response.content})
    

    
    return render(request, 'chatroom.html', context)