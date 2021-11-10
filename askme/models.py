from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.postgres.search import SearchVector

class QuestionManager(models.Manager):
    def hot(self):
        return super().get_queryset().annotate(num_likes=Count('likes')).order_by('-num_likes', '-created',)

    def last(self):
        return super().get_queryset().order_by('-created')

    def by_tag(self, tag:str):
        return super().get_queryset().filter(tag__name__contains=tag).order_by('-created')

    def by_query(self, query:str):
        sv = SearchVector('tag__name', 'title', 'description')
        return super().get_queryset().annotate(search=sv).filter(search=query).order_by('-created')


class UserManager(models.Manager):
    def best(self):
        return super().get_queryset().annotate(num_likes=Count('user__question_like') + Count('user__answer_like')).order_by('-num_likes')


class TagManager(models.Manager):
    def best(self, start, end):
        return super().get_queryset().filter(questions__created__range=[start, end]).annotate(number_of_questions=Count('questions')).order_by('-number_of_questions')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars', default='avatars/person-dummy.jpg')
    nick = models.CharField(max_length=50, null=True)
    objects = UserManager()

class Question(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='question_like')
    objects = QuestionManager()

class Tag(models.Model):
    name = models.CharField(max_length=20)
    questions = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    objects = TagManager()

class Answer(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    is_correct = models.BooleanField(default=False)
    text = models.CharField(max_length=500)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='answer_like')