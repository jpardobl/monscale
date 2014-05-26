import sys, simplejson
from django.core.management.base import BaseCommand
from django.conf import settings
from monscale.models import MonitoredService, ScaleAction, Threshold, ServiceInfrastructure
from monscale.utils import import_data

class Command(BaseCommand):
    args = ''
    help = 'Imports json file with monitoring services'



    def handle(self, *args, **options):
        #[x.delete() for x in ScaleAction.objects.all()]
        #[x.delete() for x in Threshold.objects.all()]
        #[x.delete() for x in MonitoredService.objects.all()]
        try:
            path = sys.argv[2]
            with open(path) as f: data = f.read()
            print data

            import_data(data)
        except IOError:
            self.stderr.write("Error reading data json file: %s" % path)
            exit(1)
            

