from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.files.images import ImageFile
import django.contrib.auth as djauth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Count

from .models import UserProfile, Question, Tag, Answer, Like
from .forms import LoginForm, RegisterForm, AddQuestionForm, AddAnswerForm, SettingsForm
from .settings import MEDIA_ROOT
from .utils import cropper

from PIL import Image

def index(request):
    pg = Paginator(Question.objects.order_by('-created').all(), 4)
    page = request.GET.get('page', 1)
    try:
        qp = pg.page(page)
    except PageNotAnInteger:
        qp  = pg.page(1)
    except EmptyPage:
        qp = pg.page(pg.num_pages)
    return render(request, 'index.html', {'title': 'Новые вопросы', 'quests': qp})

def search(request):
    query = request.GET.get('query')
    if not query:
        return HttpResponseRedirect('/')
    pg = Paginator(Question.objects.filter(tags__name__contains=query).order_by('-created').all(), 4)
    page = request.GET.get('page', 1)
    try:
        qp = pg.page(page)
    except PageNotAnInteger:
        qp  = pg.page(1)
    except EmptyPage:
        qp = pg.page(pg.num_pages)
    return render(request, 'index.html', {'title': 'Поиск', 'quests': qp})

def hot_questions(request):
    pg = Paginator(Question.objects.annotate(num_likes=Count('like')).order_by('-num_likes'), 4)
    page = request.GET.get('page', 1)
    try:
        qp = pg.page(page)
    except PageNotAnInteger:
        qp  = pg.page(1)
    except EmptyPage:
        qp = pg.page(pg.num_pages)
    return render(request, 'index.html', {'title': 'Горячие вопросы', 'quests': qp})

def logout(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    djauth.logout(request)
    return HttpResponseRedirect('/')

def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if not User.objects.filter(username=data['login']).exists():
                messages.error(request, f'Пользователь {data["login"]} не существует.')
                return HttpResponseRedirect('/')

            user = authenticate(username=data['login'], password=data['passw'])
            if user is not None:
                userprofile = User
                messages.info(request, "Успешный вход.")
                djauth.login(request, user)
                return HttpResponseRedirect('/')
            else:
                messages.error(request, f'Неверный пароль.')
                return HttpResponseRedirect('/')
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect('/')
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():        
            data = form.cleaned_data

            if User.objects.filter(username=data['login']).exists():
                messages.error(request, f'Пользователь {data["login"]} уже существует.')
                return HttpResponseRedirect('/')
                
            if data['passw'] != data['passw_conf']:
                messages.error(request, 'Пароли не совпадают.')
                return HttpResponseRedirect('/')

            newavatar = request.FILES['avatar']
            newavatar = cropper(newavatar, newavatar.name)
            userprofile = UserProfile()
            userprofile.avatar = newavatar
            userprofile.nick = data['nick']
            user = User.objects.create_user(username=data['login'], email=data['email'], password=data['passw'])
            userprofile.user = user
            userprofile.save()
            user = authenticate(username=data['login'], password=data['passw'])
            if user is not None:
                djauth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect('/')
    else:
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

def add_question(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        print('ПРИНЯТ POST')
        form = AddQuestionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if request.user.is_authenticated and User.objects.filter(username=request.user).exists():
                user = User.objects.get(username=request.user)
                profile = UserProfile.objects.get(user=user)
                q = Question()
                q.title = data['title']
                q.description = data['text']
                q.user = profile
                q.save()
                tags = data['tags']
                tags = tags.split(',') if ',' in tags else [tags]
                for tag in tags:
                    if not Tag.objects.filter(name=tag).exists():
                        t = Tag()
                        t.name = tag
                        t.save()
                    else:
                        t = Tag.objects.get(name=tag)
                    q.tags.add(t)
                q.save()
                messages.info(request, "Вопрос успешно добавлен.")
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'Пользователь не существует.')
                return HttpResponseRedirect('/')
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect('/')
    else:
        form = AddQuestionForm()
        return render(request, 'add.html', {'form': form})

def like_question(request, id=None):
    if not request.user.is_authenticated or not id:
        return HttpResponseRedirect('/')
    q = Question.objects.get(id=id)
    user = User.objects.get(username=request.user)
    profile = UserProfile.objects.get(user=user)
    like, created = Like.objects.get_or_create(user=profile, question=q)
    if not created:
        like.user = profile
        like.question = q
        like.save()
    return HttpResponseRedirect('/')

def like_answer(request, q_id=None, a_id=None):
    if not request.user.is_authenticated or not a_id:
        return HttpResponseRedirect('/')
    q = Question.objects.get(id=q_id)
    a = Answer.objects.get(id=a_id)
    user = User.objects.get(username=request.user)
    profile = UserProfile.objects.get(user=user)
    like, created = Like.objects.get_or_create(user=profile, answer=a)
    if not created:
        like.user = profile
        like.answer = a
        like.save()
    return HttpResponseRedirect('/')

def question(request, id=None):
    if not request.user.is_authenticated or not id:
        return HttpResponseRedirect('/')
    q = Question.objects.get(id=id)
    pg = Paginator(q.answer_set.order_by('-created').all(), 4)
    page = request.GET.get('page', 1)
    try:
        pa = pg.page(page)
    except PageNotAnInteger:
        pa  = pg.page(1)
    except EmptyPage:
        pa = pg.page(pg.num_pages)
    if request.method == 'POST':
        form = AddAnswerForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if request.user.is_authenticated and User.objects.filter(username=request.user).exists():
                user = User.objects.get(username=request.user)
                profile = UserProfile.objects.get(user=user)
                a = Answer()
                a.text = data['text']
                a.user = profile
                a.question = q
                a.save()
                messages.info(request, "Ответ успешно добавлен.")
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'Вы не авторизованы.')
                return HttpResponseRedirect('/')
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect('/')
    else:
        form = AddAnswerForm()
    return render(request, 'question.html', {'quest': q, 'answers': pa, 'form': form})

def settings(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)
        if form.is_valid():        
            data = form.cleaned_data
            newavatar = request.FILES['avatar']
            newavatar = cropper(newavatar, newavatar.name)
            user = User.objects.get(username=request.user)
            userprofile = UserProfile.objects.get(user=user)
            username_changed = user.username != data['login']
            user.username = data['login']
            user.email = data['email']
            userprofile.avatar = newavatar
            userprofile.nick = data['nick']
            userprofile.save()
            if username_changed:
                user = authenticate(username=data['login'], password=user.password)
            return HttpResponseRedirect('/')
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect('/')
    else:
        form = SettingsForm()
        return render(request, 'settings.html', {'form': form})