import sys, simplejson
from django.core.management.base import BaseCommand
from django.conf import settings
from monscale.models import MonitoredService, ScaleAction, Threshold


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
            
            services = []
            actions, thresholds = (0 , 0)

            for obj in simplejson.loads(data):                
                if obj["type"] == u"ScaleAction": 
                    ScaleAction.from_json(simplejson.dumps(obj))
                    actions += 1
                    continue
                if obj["type"] == u"Threshold": 
                    thresholds += 1
                    Threshold.from_json(simplejson.dumps(obj))
                    continue
                services.append(obj)
                
            for service in services:
                MonitoredService.from_json(simplejson.dumps(service))
                    
            self.stdout.write("Successfully imported %s actions, %s thresholds, %s services" %(
                actions, thresholds, len(services)))
        except IndexError: 
            self.stderr.write("Need to supply path to data json file")
            exit(1)
        except IOError:
            self.stderr.write("Error reading data json file: %s" % path)
            exit(1)

