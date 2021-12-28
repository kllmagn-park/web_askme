from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from .settings import STATIC_URL

import pgtrigger

class QuestionManager(models.Manager):
    # super().get_queryset()
    def last(self):
        return super().get_queryset().order_by('-created')

    def hot(self):
        return self.last().annotate(num_likes=Count('likes')).order_by('-num_likes') #order_by('-num_likes', '-created',)

    def by_tag(self, tag:str):
        return self.last().filter(tag__name__contains=tag) #.filter(tag__name__contains=tag).order_by('-created')

    def by_query(self, query:str):
        return self.last().filter(sv=query) #.order_by('-created')

class UserManager(models.Manager):
    def best(self):
        return super().get_queryset().annotate(num_quest_likes=Count('question_like'), num_ans_likes=Count('answer_like'))\
            .annotate(num_likes=F('num_quest_likes')+F('num_ans_likes'))\
            .order_by('-num_likes')[:10]

class TagManager(models.Manager):
    def best(self, start, end):
        return super().get_queryset().filter(questions__created__range=[start, end]).annotate(number_of_questions=Count('questions')).order_by('-number_of_questions')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars', default=STATIC_URL+'img/person-dummy.jpg')
    nick = models.CharField(max_length=50, null=True)
    friends = models.ManyToManyField('self')
    objects = UserManager()

class Question(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(UserProfile, related_name='question_like')
    sv = SearchVectorField(null=True)
    objects = QuestionManager()
    class Meta:
        indexes = [GinIndex(fields=['sv'])]
    def __str__(self):
        return f"{self.user.user.username} {self.title} {self.description} | {self.likes.count()} | {self.created}"

class Tag(models.Model):
    name = models.CharField(max_length=20)
    questions = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    objects = TagManager()
    def __str__(self):
        return self.name

class Answer(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    is_correct = models.BooleanField(default=False)
    text = models.CharField(max_length=500)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(UserProfile, related_name='answer_like')
    def __str__(self):
        return f"{self.user.user.username} {self.text} | {self.likes.count()} | {self.created} {self.is_correct}"