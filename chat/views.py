from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Chat, Message
from core.models import Course
from django.contrib.auth.decorators import login_required
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from operator import add as add_messages
from typing import TypedDict, Annotated, Sequence

from .study_buddy_ai import create_agent


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



'''
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage

load_dotenv()
llm = ChatDeepSeek(model="deepseek-chat")
'''

def convert_message(messages):
    existing_messages = []
    for message in messages:
        match message.role:
            case "system":
                existing_messages.append(SystemMessage(content=message.content))
            case "human":
                existing_messages.append(HumanMessage(content=message.content))
            case "ai":
                existing_messages.append(AIMessage(content=message.content))
            case "tool":
                existing_messages.append(ToolMessage(content=message.content))
    
    return existing_messages

@login_required
def chatroom(request, chat_id):
    # Load original chat
    chat = Chat.objects.get(id=chat_id)
    messages = Message.objects.filter(chat=chat).order_by('created_at')
    existing_messages = convert_message(messages)

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
    
    agent = create_agent()



    '''
    if request.method == "POST":
        user_message = request.POST.get("message") + " DO NOT USE MARKDOWN!";
        response = llm.invoke([HumanMessage(content=user_message)])
        return JsonResponse({'response': response.content})
    '''

    context = {
        'chat_id': chat_id,
        'messages': messages,
    }

    return render(request, 'chatroom.html', context)