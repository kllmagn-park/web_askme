from django.core.management.base import BaseCommand, CommandError
from django.core.cache import caches

from ...models import UserProfile

class Command(BaseCommand):
    help = 'Кэшировать из БД лучших пользователей'

    def add_arguments(self, parser):
        parser.add_argument('--timeout', nargs='?', const=24*60*60, type=int)

    def handle(self, *args, **options):
        caches.all()[0].set('best_users', UserProfile.objects.best(), options['timeout'])