from django.core.management.base import BaseCommand, CommandError
import os
from crontab import CronTab

class Command(BaseCommand):
    help = 'Инициализировать Сron задачи.'

    def add_arguments(self, parser):
        parser.add_argument('--timeout', nargs='?', const=24*60, type=int) # minutes

    def handle(self, *args, **options):
        #init cron
        cron = CronTab(user='jellybe')

        timeout = options['timeout'] # minutes 
        if not timeout:
            timeout = 24*60
            
        #add new cron job
        comment = 'askme_cache_bu'
        cron.remove_all(comment=comment)
        job = cron.new(command=f'./.venv/bin/python ./manage.py cache_best_users --timeout {timeout*60*5} 2>&1', comment=comment)

        #job settings
        job.minute.every(timeout)

        cron.write()