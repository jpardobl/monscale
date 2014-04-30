import logging, redis, time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from monscale.rules import evaluate_traps

class Command(BaseCommand):
    args = ''
    help = 'Retrieve queued actions and execute them.'

    def handle(self, *args, **options):
#        logging.basicConfig(level=logging.DEBUG)

        while True:
            logging.debug("[trap_worker] starting loop ...")            
            
            evaluate_traps()
            logging.debug("[trap_worker] going to sleep for %ss" % settings.ACTION_WORKER_SLEEP_SECS)
            time.sleep(settings.ACTION_WORKER_SLEEP_SECS)
