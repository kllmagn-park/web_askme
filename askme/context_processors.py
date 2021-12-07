from django.contrib.auth.models import User
from django.db.models import Count, F, Sum
from django.core.cache import caches

from .settings import SITE_TITLE, MEDIA_URL
from .models import UserProfile, Tag

from django.utils import timezone

def set_settings(request):
    return {'SITE_TITLE': SITE_TITLE, 'MEDIA_URL': MEDIA_URL}

def user_info(request):
    user = request.user
    if User.objects.filter(username=user).exists():
        user = User.objects.get(username=user)
        profile = UserProfile.objects.get(user=user)
        return {
            'myprofile': profile,
            'avatar': profile.avatar.url,
            'username': user.username,
            'usermail': user.email,
            'usernick': profile.nick
            }
    else:
        return {}

def best_users(request):
    busers = caches.all()[0].get('best_users')
    return {'best_users': busers}

def tags_rank(request):
    tags = Tag.objects.all()
    end = timezone.now()
    start = end - timezone.timedelta(days=90) # последние 3 месяца
    rank = Tag.objects.best(start, end)
    if rank.count() > 10:
        rank = rank[:10]
    return {'tags_rank': rank}