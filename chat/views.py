from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Chat, Message
from core.models import Course
from django.contrib.auth.decorators import login_required
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from .study_buddy_ai.agent import create_agent
from django.utils import timezone

# Create your views here.

'''
Chat
'''
@login_required
def chat(request):
    chats = Chat.objects.filter(user=request.user).order_by('-last_message_time')
    context = {
        'chats': chats,
    }

    return render(request, 'chat.html', context)

@login_required
def create_chat(request):
    if request.method == "POST":
        chat = Chat(user=request.user)
        chat.title = "New Chat"
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
    this_chat = Chat.objects.get(id=chat_id, user=request.user)
    messages = Message.objects.filter(chat=this_chat).order_by('created_at')
    chats = Chat.objects.filter(user=request.user).order_by('-last_message_time')


    if request.method == "POST":
        existing_messages = convert_message(messages)
        agent = create_agent()
        user_message = request.POST["message"]
        new_state = agent.invoke({"messages": existing_messages + [HumanMessage(content=user_message)], "request": request})
        ai_message = new_state['messages'][-1].content

        # Save to database
        Message.objects.create(chat=this_chat, role="human", content=user_message)
        Message.objects.create(chat=this_chat, role="ai", content=ai_message)

        # Update chat last message timestamp
        this_chat.last_message_time = timezone.now()
        this_chat.save(update_fields=['last_message_time'])

        return JsonResponse({"response": ai_message})
    
    context = {
        'chat_id': chat_id,
        'messages': messages,
        'chats': chats,
    }

    return render(request, 'chatroom.html', context)

@login_required
def change_chat_name(request):
    if request.method == "POST":
        chat_id = request.POST["chat_id"]
        new_name = request.POST["new_name"]

        chat = Chat.objects.get(user=request.user, id=chat_id)
        chat.title = new_name
        chat.save()

    return JsonResponse({'message': 'success'}) 