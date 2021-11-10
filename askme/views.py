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

from .models import UserProfile, Question, Tag, Answer
from .forms import LoginForm, RegisterForm, AddQuestionForm, AddAnswerForm, SettingsForm
from .settings import MEDIA_ROOT
from .utils import cropper, _like, _set_correct, _login, _form_ask, _form_question, _form_settings, _form_signup

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

def index(request):
    qp = paginate(Question.objects.last(), request, 4)
    return render(request, 'index.html', {'title': 'Новые вопросы', 'quests': qp})

def show_tag(request, tag):
    qp = paginate(Question.objects.by_tag(tag), request, 4)
    return render(request, 'index.html', {'title': 'Тег - ' + tag, 'quests': qp})

def search(request):
    query = request.GET.get('query')
    if not query:
        return HttpResponseRedirect(reverse('index'))
    qp = paginate(Question.objects.by_query(query), request, 4)
    return render(request, 'index.html', {'title': 'Поиск', 'quests': qp})

def hot_questions(request):
    qp = paginate(Question.objects.hot(), request, 4)
    return render(request, 'index.html', {'title': 'Горячие вопросы', 'quests': qp})

def logout(request):
    if request.user.is_authenticated:
        djauth.logout(request)
    return HttpResponseRedirect(reverse('index'))

def login(request, redirect_url=None):
    redirect = redirect_url if redirect_url else '/'
    if redirect_url or request.user.is_authenticated:
        return HttpResponseRedirect(redirect)
    return _login(request)

def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    return _form_signup(request)

def ask(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return _form_ask(request)

def like(request):
    if not request.user.is_authenticated:
        raise Http404
    if request.method != 'POST':
        raise Http404
    info = _like(request)
    return HttpResponse(json.dumps(info), content_type='application/json')

def set_correct(request):
    if not request.user.is_authenticated:
        raise Http404
    if request.method != 'POST':
        raise Http404
    _set_correct(request)
    return HttpResponse('OK')

def question(request, id=None):
    if not id: # id вопроса не предоставлен, перенаправляем на главную
        return HttpResponseRedirect('/')
    return _form_question(request, id)

def settings(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return _form_settings(request)

def handler404(request, exception, template_name="404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response