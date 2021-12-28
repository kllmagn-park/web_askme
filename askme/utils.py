from PIL import Image
from io import BytesIO

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from .models import UserProfile, Question, Tag, Answer

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.files.images import ImageFile
import django.contrib.auth as djauth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Count, F, Sum
from django.shortcuts import render
from django.urls import reverse
from django.contrib.postgres.search import SearchVector

from .models import UserProfile, Question, Tag, Answer
from .forms import LoginForm, RegisterForm, AddQuestionForm, AddAnswerForm, SettingsForm

from PIL import Image
import json
import re


def paginate(objs, request, per_page=4):
    pg = Paginator(objs, per_page)
    page = request.GET.get('page', 1)
    try:
        pgp = pg.page(page)
    except PageNotAnInteger:
        pgp = pg.page(1)
    except EmptyPage:
        pgp = pg.page(pg.num_pages)
    return pgp

def cropper(original_image, name):
    img_io = BytesIO()
    im = Image.open(original_image)
    width, height = im.size
    new_width = new_height = min(width, height)
    left = (width - new_width)/2
    top = (height - new_height)/2
    right = (width + new_width)/2
    bottom = (height + new_height)/2
    im = im.crop((left, top, right, bottom)).resize((200, 200), Image.ANTIALIAS)
    im.save(img_io, format='JPEG', quality=100)
    img_content = ContentFile(img_io.getvalue(), name)
    return img_content

def _login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if not User.objects.filter(username=data['login']).exists():
                messages.error(request, f'Пользователь {data["login"]} не существует.')
                return HttpResponseRedirect(reverse('login'))

            user = authenticate(username=data['login'], password=data['passw'])
            if user is not None:
                userprofile = User
                messages.info(request, "Успешный вход.")
                djauth.login(request, user)
                return HttpResponseRedirect("%s?continue=/" % reverse("login"))
            else:
                messages.error(request, f'Неверный пароль.')
                return HttpResponseRedirect(reverse('login'))
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect(reverse('login'))
    else:
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

def _like(request) -> dict:
    '''
    Поставить лайк посту или убрать лайк у поста (у ответа/вопроса).
    '''
    q_id = request.POST.get('q_id')
    a_id = request.POST.get('a_id')
    if q_id:
        post = get_object_or_404(Question, id=q_id)
    elif a_id:
        post = get_object_or_404(Answer, id=a_id)
    else:
        raise Http404
    userp = UserProfile.objects.get(user=request.user)
    if post.likes.filter(user=request.user).exists():
        post.likes.remove(userp)
    else:
        post.likes.add(userp)
    return {'likes_count': post.likes.count()}


def _set_correct(request):
    '''
    Пометить ответ как корректный/убрать пометку.
    '''
    a_id = request.POST.get('a_id')
    if not a_id:
        raise Http404
    answer = get_object_or_404(Answer, id=a_id)
    if str(answer.question.user.user.username) != str(request.user):
        raise Http404
    if not answer.is_correct: # если обновляемый ответ нееверный (будет верным)
        # помечаем все остальные ответы как неверные
        Answer.objects.filter(is_correct=True, question=answer.question).update(is_correct = False)
    answer.is_correct = not answer.is_correct # переключаем ответ (верный/неверный)
    answer.save()
    print(answer)


def _profile(request):
    if request.method != 'GET': return HttpResponseRedirect(reverse('index'))
    user_id = request.GET.get('id')
    if not user_id and request.user.is_authenticated:
        user_id = User.objects.filter(username=request.user).first()
        if user_id:
            user_id = user_id.id
    if not user_id: return HttpResponseRedirect(reverse('index'))
    user = User.objects.filter(id=user_id).first()
    if not user: return HttpResponseRedirect(reverse('index'))
    userp = UserProfile.objects.filter(user=user).first()
    if not userp: return HttpResponseRedirect(reverse('index'))
    return render(request, 'profile.html', {'profile': userp})


def _form_settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)
        if form.is_valid():        
            data = form.cleaned_data
            user = User.objects.get(username=request.user)
            userprofile = UserProfile.objects.get(user=user)
            username_changed = 'login' in data and user.username != data['login']
            if 'login' in data:
                user.username = data['login']
            if 'email' in data:
                user.email = data['email']
            user.save()
            if 'avatar' in request.FILES:
                newavatar = request.FILES['avatar']
                newavatar = cropper(newavatar, newavatar.name)
                userprofile.avatar = newavatar
            if 'nick' in data:
                userprofile.nick = data['nick']
            userprofile.save()
            if username_changed:
                user = authenticate(username=data['login'], password=user.password)
            return HttpResponseRedirect(reverse('settings'))
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect(reverse('settings'))
    else:
        user = User.objects.get(username=request.user)
        profile = UserProfile.objects.get(user=request.user)
        form = SettingsForm(initial={
            'login': user.username,
            'email': user.email,
            'nick': profile.nick
            })
        return render(request, 'settings.html', {'form': form})


def _form_question(request, id=None):
    q = Question.objects.get(id=id)
    pa = paginate(q.answer_set.order_by('-is_correct', '-created').all(), request, 4)
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
                return HttpResponseRedirect(reverse('question', kwargs={'id': id}))
            else:
                messages.error(request, 'Вы не авторизованы.')
                return HttpResponseRedirect(reverse('login'))
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect(reverse('question', kwargs={'id': id}))
    else:
        form = AddAnswerForm()
    return render(request, 'question.html', {'quest': q, 'answers': pa, 'form': form})


def _form_ask(request):
    if request.method == 'POST':
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
                tags = re.sub(r'(?:(?<=\,)\s*|\s*(?=\,))','', tags)
                tags = tags.split(',') if ',' in tags else [tags]
                for tag in tags:
                    if not Tag.objects.filter(name=tag).exists():
                        t = Tag()
                        t.name = tag
                        t.save()
                    else:
                        t = Tag.objects.get(name=tag)
                    q.tag_set.add(t)
                q.save()
                Question.objects.filter(pk=q.pk).update(sv=SearchVector('title', 'description'))
                messages.info(request, "Вопрос успешно добавлен.")
                return HttpResponseRedirect('/#q_'+str(q.id)) #reverse('question', kwargs={'id': q.id}))
            else:
                messages.error(request, 'Пользователь не существует.')
        else:
            messages.error(request,'Форма неверно заполнена.')
        return HttpResponseRedirect(reverse('ask'))
    else:
        form = AddQuestionForm()
        return render(request, 'ask.html', {'form': form})

def _form_signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():        
            data = form.cleaned_data
            if User.objects.filter(username=data['login']).exists():
                messages.error(request, f'Пользователь {data["login"]} уже существует.')
                return HttpResponseRedirect(reverse('signup'))
            if data['passw'] != data['passw_conf']:
                messages.error(request, 'Пароли не совпадают.')
                return HttpResponseRedirect(reverse('signup'))
            userprofile = UserProfile()
            if 'avatar' in request.FILES:
                newavatar = request.FILES['avatar']
                newavatar = cropper(newavatar, newavatar.name)
                userprofile.avatar = newavatar
            userprofile.nick = data['nick']
            user = User.objects.create_user(username=data['login'], email=data['email'], password=data['passw'])
            userprofile.user = user
            userprofile.save()
            user = authenticate(username=data['login'], password=data['passw'])
            if user is not None:
                djauth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(request,'Форма неверно заполнена.')
            return HttpResponseRedirect(reverse('signup'))
    else:
        form = RegisterForm()
        return render(request, 'signup.html', {'form': form})