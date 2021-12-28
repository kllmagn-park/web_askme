"""askme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from . import views
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),                            # панель управления
    path('', views.index, name='index'),                                      # главная страница
    path('hot/', views.hot_questions, name='hot'),                            # популярные вопросы
    path('signup/', views.signup, name='signup'),                             # регистрация
    path('login/', views.login, name='login'),                                # вход - перенаправление
    path('logout/', views.logout, name='logout'),                             # выход
    path('ask/', views.ask, name='ask'),                                      # задать вопрос
    path('like', views.like, name='like'),                                    # поставить лайк
    path('set_correct', views.set_correct, name='set_correct'),               # пометить ответ как верный
    path('question/<int:id>/', views.question, name='question'),              # страница вопроса
    path('search/', views.search, name='search'),                             # поиск
    path('tag/<str:tag>', views.show_tag, name='tag'),                        # страница вопросов с тегом
    path('profile/', views.profile, name='profile'),                           # профиль
    path('profile/edit/', views.settings, name='settings'),                   # настройки пользователя
    path('profile/add', views.handle_friend, name='add_friend'),              # добавить/удалить друга

    path('game/', views.game, name='game')                                    # игра
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

handler404 = 'askme.views.handler404'