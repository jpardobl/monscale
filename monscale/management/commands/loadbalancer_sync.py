import logging, redis, time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from monscale.loadbalancers import synclb

logger = logging.getLogger("loadbalancer_sync")
logger.setLevel(settings.LOG_LEVEL)


class Command(BaseCommand):
    args = ''
    help = 'Retrieve queued actions and execute them.'

    def handle(self, *args, **options):

        while True:
            logger.debug("[loadbalancer_sync] starting loop ...")

            try:
                synclb()
            except Exception as er:
                logger.error("[loadbalancer_sync] ERROR caught at daemon loop level: %s" % er)

            logger.debug("[loadbalancer_sync] going to sleep for %ss" % settings.ACTION_WORKER_SLEEP_SECS)
            time.sleep(settings.ACTION_WORKER_SLEEP_SECS)
