from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Chat, Message
from core.models import Course
from django.contrib.auth.decorators import login_required
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from .study_buddy_ai.agent import create_agent

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


def convert_message(messages):
    existing_messages = []
    for message in messages:
        match message.role:
            case "human":
                existing_messages.append(HumanMessage(content=message.content))
            case "ai":
                existing_messages.append(AIMessage(content=message.content))
    
    return existing_messages

@login_required
def chatroom(request, chat_id):
    # Load original chat
    chat = Chat.objects.get(id=chat_id, user=request.user)
    messages = Message.objects.filter(chat=chat).order_by('created_at')

    if request.method == "POST":
        existing_messages = convert_message(messages)
        agent = create_agent()
        user_message = request.POST["message"]
        new_state = agent.invoke({"messages": existing_messages + [HumanMessage(content=user_message)], "request": request})
        ai_message = new_state['messages'][-1].content

        # Save to database
        Message.objects.create(chat=chat, role="human", content=user_message)
        Message.objects.create(chat=chat, role="ai", content=ai_message)

        return JsonResponse({"response": ai_message})
    
    context = {
        'chat_id': chat_id,
        'messages': messages,
    }

    return render(request, 'chatroom.html', context)