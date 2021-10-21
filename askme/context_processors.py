from django.contrib.auth.models import User
from django.db.models import Count

from .settings import SITE_TITLE # import the settings file
from .models import UserProfile, Tag


def site_title(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'SITE_TITLE': SITE_TITLE}

def user_info(request):
    user = request.user
    if User.objects.filter(username=user).exists():
        user = User.objects.get(username=user)
        profile = UserProfile.objects.get(user=user)
        return {
            'avatar': profile.avatar.url,
            'username': user.username,
            'usermail': user.email,
            'usernick': profile.nick
            }
    else:
        return {}

def best_users(request):
    busers = UserProfile.objects.annotate(num_likes=Count('like')).order_by('-num_likes')
    if busers.count() > 10:
        busers = busers[:10]
    return {'best_users': busers}

    
def tags_rank(request):
    tags = Tag.objects.all()
    rank = tags.annotate(number_of_questions=Count('question')).order_by('-number_of_questions')
    if rank.count() > 20:
        rank = rank[:30]
    return {'tags_rank': rank}