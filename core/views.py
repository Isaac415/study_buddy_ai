from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Course, Document, MultipleChoiceQuestion, ShortQuestion, Quiz
import os
from django.conf import settings
from supabase import create_client
from dotenv import load_dotenv
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json


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
@login_required
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

@login_required
def course_detail(request, course_id):
    courses = Course.objects.filter(user=request.user)
    this_course = Course.objects.get(user=request.user, id=course_id)

    context = {
        'courses': courses,
        'this_course': this_course,
    }

    return render(request, 'course_detail.html', context)


@login_required
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

        return redirect(f'/course/{course.id}')

'''
Document
'''
@login_required
def document(request):
    courses = Course.objects.filter(user=request.user)
    documents = Document.objects.filter(user=request.user)
    context = {
        'courses': courses,
        'documents': documents
    }
    return render(request, 'document.html', context)

def supabase_client():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)

    return supabase

def create_embedding(text: str):
    supabase = supabase_client()
    response = supabase.functions.invoke("create-embedding", 
                                    invoke_options={"body": {"text": text}})
    embedding = json.loads(response.decode('utf-8'))
    
    return embedding

@login_required
def upload_document(request):
    if request.method == 'POST':
        description = request.POST['description'].strip()
        course = request.POST['course']
        file = request.FILES.get('file')

        # Save file to local temp
        temp_dir = os.path.join(settings.BASE_DIR, 'temp')
        filename = f"{request.user.username}_{file.name}"
        local_file_path = os.path.join(temp_dir, filename)

        with open(local_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Save to Supabase
        supabase = supabase_client()
        supabase_path = f"{request.user.username}/{int(time.time())}_{file.name}"
        file.seek(0)
        file_data = file.read()
        supabase_res = supabase.storage.from_('user-uploads').upload(supabase_path, file_data)

        # Save a Document record to database
        course_obj = Course.objects.get(user=request.user, name=course)
        document = Document(description=description,
                            original_filename=file.name,
                            user=request.user,
                            course=course_obj,
                            url=supabase_res.path)
        document.save()

        # Load, split, create embeddings, and save to vector store
        pdf_loader = PyPDFLoader(local_file_path)
        pages = pdf_loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=128,
        )
        pages_split = text_splitter.split_documents(pages)

        for part in pages_split:
            embedding = create_embedding(part.page_content)
            supabase.table("vector-store").insert({
                "chunk": part.page_content,
                "embedding": embedding,
                "document_id": document.id,
                "user_id": request.user.id,
            }).execute()

        # Delete local temp file
        os.remove(local_file_path)

        return redirect('/document')

'''
Quiz
'''
@login_required
def quiz(request):
    quizzes = Quiz.objects.filter(user=request.user)
    documents = Document.objects.filter(user=request.user)
    context = {
        'quizzes': quizzes,
        'documents': documents,
    }

    return render(request, 'quiz.html', context)


@login_required
def create_mc(request):
    if request.method == 'POST':
        question = request.POST['question']
        choice_1 = request.POST['choice_1']
        choice_2 = request.POST['choice_2']
        choice_3 = request.POST['choice_3']
        choice_4 = request.POST['choice_4']
        correct_ans = int(request.POST['correct_ans'])
        explanation = request.POST['explanation']
        document_id = request.POST['document']
        document = Document.objects.get(id=document_id, user=request.user)
        mcq = MultipleChoiceQuestion.objects.create(
            user=request.user,
            document=document,
            question=question,
            choice_1=choice_1,
            choice_2=choice_2,
            choice_3=choice_3,
            choice_4=choice_4,
            correct_ans=correct_ans,
            explanation=explanation,
        )
        return redirect('/quiz')

@login_required
def take_quiz(request, quiz_id):
    quiz = Quiz.objects.get(user=request.user, id=quiz_id)
    context = {
        'quiz': quiz
    }

    return render(request, 'take_quiz.html', context)