import simplejson
from monscale.models import *

def import_data(data):

    try:
        services = []
        actions, thresholds, infrastructures = (0 , 0, 0)

        for obj in simplejson.loads(data):                
            if obj["type"] == u"ScaleAction": 
                ScaleAction.from_json(simplejson.dumps(obj))
                actions += 1
                continue
            if obj["type"] == u"Threshold": 
                thresholds += 1
                Threshold.from_json(simplejson.dumps(obj))
                continue
            if obj["type"] == u"ServiceInfrastructure": 
                infrastructures += 1
                ServiceInfrastructure.from_json(simplejson.dumps(obj))
                continue
            services.append(obj)
                
        for service in services:
            MonitoredService.from_json(simplejson.dumps(service))
                    
        logging.debug("Successfully imported %s actions, %s thresholds, %s services, %s infrastructures" %(
                actions, thresholds, len(services), infrastructures))
    except IndexError: 
        logging.error("Need to supply path to data json file")
        exit(1) 
