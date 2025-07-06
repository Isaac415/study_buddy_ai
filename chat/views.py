from django.shortcuts import render
from django.http import JsonResponse

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage

# Create your views here.
load_dotenv()
llm = ChatDeepSeek(model="deepseek-chat")

'''
Chat
'''
def chat(request):
    # Handles chat message
    if request.method == "POST":
        user_message = request.POST.get("message") + " DO NOT USE MARKDOWN!";
        response = llm.invoke([HumanMessage(content=user_message)])
        return JsonResponse({'response': response.content})
    

    
    return render(request, 'chat.html')