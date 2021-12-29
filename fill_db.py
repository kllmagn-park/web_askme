import os
import random
from random import randrange
from datetime import timedelta, datetime
import string
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'askme.settings')
django.setup()
from askme.models import *

from mimesis.locales import Locale
from mimesis import Person
from xml.etree import ElementTree
import requests
import nltk
from nltk.collocations import *

from itertools import islice
import itertools

PARSE_URL = f'http://db.chgk.info/xml/random'

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def get_data(num=999):
    url = PARSE_URL + f'/limit{num}'
    BAD_CHARS = ":.!?,\'\""
    res = requests.get(url)
    text = res.content
    doc = ElementTree.fromstring(text)
    data = []
    for child in doc:
        desc = child[8].text.replace('\n', ' ')
        if len(desc) > 500:
            desc = desc[:500]
        answer = child[9].text.replace('\n' , ' ')
        if len(answer) > 500:
            answer = answer[:500]
        if len(desc) > 20:
            title = desc[:20]
        else:
            title = desc
        title += '...'
        tags = list(filter(lambda x: len(x) > 5 and len(x) < 20 and not any([c in x for c in BAD_CHARS]), desc.split(' ')))
        if len(tags) > 3:
            tags = tags[:3]
        data.append({'question': {'title': title, 'description': desc, 'tags': tags}, 'answer': answer})
    return data

locale = Locale.RU

def fill(fill_users=True, fill_questions=True, fill_tags=True, fill_answers=True, fill_likes=True):
    USERS_TO_FILL = 100000
    LIKES = 2000000
    batch_size = 1000

    if fill_users and fill_questions and fill_tags and fill_answers and fill_likes:
        print('Очищаю базу данных... ', end='')
        Tag.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        print('очищено!')

    person = Person()
    userprofiles = []
    users = []
    questions = []
    answers = []
    tags = []
    used_unames = []

    if fill_users:
        for i in range(USERS_TO_FILL):
            print(f"Записываю пользователей: {i+1} из {USERS_TO_FILL}"+" "*20, end='\r')
            uname = person.username()
            if uname in used_unames:
                uname += ''.join(random.choices(string.digits+string.ascii_letters, k=10))
            users.append(User(
                username = uname,
                email = person.email(),
                password = person.password()
            ))
            used_unames.append(uname)
       
        print('\nСоздаю записи... ', end='')
        '''
        while True:
            batch = list(islice(users, batch_size))
            if not batch:
                break
        '''
        User.objects.bulk_create(users, batch_size)
        print('готово!')
        user_objs = User.objects.all()
        for i in range(USERS_TO_FILL):
            print(f"Записываю профили: {i+1} из {USERS_TO_FILL}"+" "*20, end='\r')
            userprofiles.append(UserProfile(
                nick = person.name(),
                user = user_objs[i]
            ))
        print()
        print('Создаю записи... ', end='')
        '''
        while True:
            batch = list(islice(userprofiles, batch_size))
            if not batch:
                break
        '''
        UserProfile.objects.bulk_create(userprofiles, batch_size)
        print('готово!')

    user_objs = User.objects.all()
    userp_objs = UserProfile.objects.all()

    if fill_questions or fill_answers or fill_tags:
        print('Получаю данные из внешнего источника...')
        data = []
        for i in range(100):
            data.extend(get_data())
            print(f"Получено: {i+1} из {100}"+" "*20, end='\r')
        print()

    if fill_questions:
        print('Добавляю вопросы...', end='')
        for i in range(len(data)):
            questions.append(
                Question(
                    user = userp_objs[random.randrange(0, len(userp_objs)-1)],
                    title = data[i]['question']['title'],
                    description = data[i]['question']['description'],
                    created = random_date(datetime(2008, 8, 16), datetime.now())
                )
            )
        '''
        while True:
            batch = list(islice(questions, batch_size))
            if not batch:
                break
        '''
        Question.objects.bulk_create(questions, batch_size)
        print('готово!')

    q_objs = Question.objects.all()

    if fill_tags:
        print('Добавляю теги...', end='')
        for i in range(len(data)):
            tgs = data[i]['question']['tags']
            for j in range(len(tgs)):
                tags.append(
                    Tag(
                        name = tgs[j],
                        questions=q_objs[random.randrange(0, len(q_objs)-1)]
                    )
                )
        '''
        while True:
            batch = list(islice(tags, batch_size))
            if not batch:
                break
        '''
        Tag.objects.bulk_create(tags, batch_size)
        print('готово!')

    if fill_answers:
        print('Создаю ответы...', end='')
        n = 0
        for j in range(10):
            for i in range(len(data)):
                answer = data[int(i)]['answer']
                answers.append(
                    Answer(
                        user = userp_objs[random.randrange(0, len(userp_objs)-1)],
                        created = random_date(datetime(2008, 8, 16), datetime.now()),
                        is_correct = random.choice([True, False]),
                        text = answer,
                        question = q_objs[random.randrange(0, len(q_objs)-1)]
                    )
                )
        '''
        while True:
            batch = list(islice(answers, batch_size))
            if not batch:
                break
        '''
        Answer.objects.bulk_create(answers, batch_size)
        print('готово!')

    if fill_likes:
        ans_objs = Answer.objects.all()
        q_objs = Question.objects.all()

        q_ids = list(Question.objects.values_list('id', flat=True))
        user_ids = User.objects.values_list('id', flat=True)
        q_count = len(q_ids)
        
        print('Лайкаю вопросы...')
        q_to_user_links = []

        def gen_user_q():
            user_id = user_ids[random.randrange(0, len(user_ids)-1)]
            q_id = q_ids[random.randrange(0, len(q_ids)-1)]
            return Question.likes.through(question_id=q_id, user_id=user_id)

        it = itertools.product(user_ids, q_ids)

        i = 0
        for comb in it:
            if i + 1 == LIKES:
                break
            print(f"Лайков: {i+1} из {LIKES}"+" "*20, end='\r')
            '''
            user_q = gen_user_q()
            while user_q in q_to_user_links:
                user_q = gen_user_q()
            '''
            user_id, q_id = comb
            user_q = Question.likes.through(question_id=q_id, user_id=user_id)
            q_to_user_links.append(user_q)
            i += 1

        Question.likes.through.objects.bulk_create(q_to_user_links, batch_size=batch_size)

        '''
        for i in range(LIKES):
            print(f"Лайков: {i+1} из {LIKES}"+" "*20, end='\r')
            q_objs[random.randrange(0, len(q_objs)-1)].likes.add(user_objs[random.randrange(0, len(user_objs)-1)])
        '''


fill(fill_users=True, fill_questions=True, fill_tags=True, fill_answers=True, fill_likes=True)
