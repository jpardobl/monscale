from monscale.models import METRICS, Threshold, MonitoredService
from monscale.mappings import get_mappings
from pypelib.RuleTable import RuleTable
import logging
from django.conf import settings

import logging, datetime
from pytz import timezone
from django.conf import settings
from monscale.models import AlarmIndicator


def set_indicator(ctxt):
    service = ctxt["service"]
    logging.debug("[set_indicator] Entering for service: %s ..." % service)    
    
    indicator, db = AlarmIndicator.objects.get_or_create(service=service)
    if not db: indicator.save()
    
    now = datetime.datetime.utcnow().replace(tzinfo = timezone(settings.TIME_ZONE))
    logging.debug("[set_indicator] Now: %s" % now)
    logging.debug("[set_indicator] Last indicator: %s" % indicator.timestamp)
    time_diff = now - indicator.timestamp
    logging.debug("[set_indicator] Time diff: %s (%ss)" % (time_diff, time_diff.total_seconds()))
    logging.debug("[set_indicator] Seconds in threshold: %s" % service.threshold.time_limit)
    #TODO Logging
    #if time the last indicator is prior to the seconds in threshold, the action is triggered
    if time_diff.total_seconds() > float(service.threshold.time_limit):
        service.action.to_redis(str(service))
        logging.debug("[set_indicator] Action: %s is queued" % service.action)
        indicator.delete()
    logging.debug("[set_indicator] exiting for service: %s" % service)
    
def evaluate():
    mappings = get_mappings()
       
    for service in MonitoredService.objects.filter(active=True):
        #logging.debug("############################################### %s ###########################" % service)
        table = RuleTable("Service Rule", mappings, "RegexParser",
             #rawfile,
            "RAWFile",
            None)
        table.setPolicy(False)
              
        table.addRule(service.to_pypelib())
        
        if settings.DEBUG:
            table.dump()
    
        try:
            ctxt = {"service": service}
            table.evaluate(ctxt)
            logging.info("[evaluate] service: %s has evaluate ALARM" % service)
            set_indicator(ctxt)
        except Exception:
            try:
                logging.debug("[evaluate] threshold has evaluate no alarm")
                service.alarm_indicators.get().delete()
            except AlarmIndicator.DoesNotExist: pass
            print("No ha cumplido para el servicio: %s" % service)


def evaluate_traps():
    mappings = get_mappings()
    while True:                
        monitored_service, rule = MonitoredService.from_redis_trap()
        if monitored_service is None: break
        
        logging.debug("[evaluate_traps] retrieved trap: %s" % trap)
        table = RuleTable("Trap rule", mappings, "RegexParser",
             #rawfile,
            "RAWFile",
            None)
        table.addRule(rule)
        
        if settings.DEBUG:  table.dump()
    
        try:
            ctxt = {"service": monitored_service}
            table.evaluate(ctxt)
            logging.info("[evaluate_traps] service: %s has evaluate ALARM" % service)
            set_indicator(ctxt)
        except Exception:
            try:
                logging.debug("[evaluate_traps] threshold has evaluate no alarm")
                monitored_service.alarm_indicators.get().delete()
            except AlarmIndicator.DoesNotExist: pass
            print("No ha cumplido para el servicio: %s" % service)
            
        logging.debug("[evaluate_traps] populated action: %s" % action)