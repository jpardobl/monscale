import logging, redis, time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from monscale.models import ScaleAction
logging.disable(logging.CRITICAL)


class Command(BaseCommand):
    args = ''
    help = 'Retrieve queued actions and execute them.'



    def handle(self, *args, **options):
        logging.basicConfig(level=logging.DEBUG)
        r = redis.StrictRedis(
                host=settings.REDIS_HOST, 
                port=settings.REDIS_PORT, 
                db=settings.REDIS_DB)
        while True:
            print("[action_worker] starting loop ...")            
            
            while True:                
                try:                
                    action, jutification = ScaleAction.from_redis()
                    action.execute(jutification)
                    
                except ValueError:
                    break

            logging.debug("[action_worker] going to sleep for %ss" % settings.ACTION_WORKER_SLEEP_SECS)
            time.sleep(settings.ACTION_WORKER_SLEEP_SECS)
