import logging, simplejson
from django.core.management.base import BaseCommand
from monscale.models import MonitoredService, ScaleAction, Threshold


class Command(BaseCommand):
    args = ''
    help = 'Dumps operational database to json'



    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        
        
        out = [ x.to_dict() for x in ScaleAction.objects.all()]
            
        out += [ x.to_dict() for x in Threshold.objects.all()]
        
        out += [ x.to_dict() for x in MonitoredService.objects.all()]
        
        self.stdout.write(simplejson.dumps(out))     