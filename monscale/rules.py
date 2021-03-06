import logging
import datetime

from pytz import timezone
from django.conf import settings

from monscale.models import MonitoredService
from monscale.mappings import get_mappings
from monscale.models import AlarmIndicator, ActionIndicator
from naman.naman.pypelib import RuleTable


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
    
    #TODO Logging
    #if time the last indicator is prior to the seconds in threshold, the action is triggered
    
    for threshold in service.threshold.all():
        logging.debug("[set_indicator] Seconds in threshold: %s" % threshold)
        if time_diff.total_seconds() < float(threshold.time_limit):
            logging.info("[set_indicator] exiting without triggering actions, reason: %s state alarm not enough time" % threshold)
            return
    #checking wisdom time is passed
    logging.debug("[set_indicator] checking wisdom time before launching any action")
    
    try:
        
        aindicator = service.action_indicators.all()[0]
        
        logging.debug("[set_indicator] ::: aindicator in DB")
        """
        If alarm indicator was found in DB means actions where trigger by its timestamp
        thus need to check wisdom time against the alarm indicator timestamp
        """
        logging.debug("[set_indicator] Last action indicator: %s" % aindicator.timestamp)
        time_diff = now - aindicator.timestamp
        logging.debug("[set_indicator] Time diff: %s (%ss)" % (time_diff, time_diff.total_seconds()))
        if time_diff.total_seconds() < float(service.wisdom_time):
            logging.info("[set_indicator] Wisdom time not over, not launching actions")
            """
            deleting threshold indicator thus, next indicator will start after the wisdom
            """
#            indicator.delete()
            return
        """
        delete the action indicator because wisdom time is over, actions must be launched
        """
        aindicator.delete()
    except: 
        logging.debug("[set_indicator] no action indicator in DB")

    try:
        current_nodes = service.infrastructure.current_nodes
        logging.debug("[set_indicator] checking scale limits, current: %s" % current_nodes)
        
        if service.scale_type == 'down' and current_nodes <= service.infrastructure.min_nodes: raise AttributeError("Escalation low limit not passed")             
        if service.scale_type == 'up' and current_nodes >= service.infrastructure.max_nodes: raise AttributeError("Escalation high limit not passed")
    except AttributeError, er:
        logging.debug("[set_indicator] scale limit not passed, current: %s" % current_nodes)
        return  
    except Exception, ex:
        logging.error("[set_indicator][scale_limit] ERROR: %s" % ex)
        return    
    logging.debug("[set_indicator] scale limits passed, launching actions")    
    #lets launch the actions
    for action in service.action.all(): 
        action.to_redis(str(service))
        logging.info("[set_indicator] Action: %s is queued" % action)
    indicator.delete()
    ActionIndicator(service=service).save()


    
    
def evaluate():
    mappings = get_mappings()
       
    for service in MonitoredService.objects.filter(active=True):
        logging.debug("[rules_evaluate]############################################### %s ###########################" % service)
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
        except Exception, er:
            try:
                logging.debug("[evaluate] threshold has evaluate no alarm: %s" % er)
                service.alarm_indicators.get().delete()
            except AlarmIndicator.DoesNotExist: pass
            print("No ha cumplido para el servicio: %s" % service)
        logging.debug("[rules_evalute] iteration ended")

def evaluate_traps():
    mappings = get_mappings()
    while True:                
        monitored_service, rule = MonitoredService.from_redis_trap()
        if monitored_service is None: break
        
        logging.debug("[evaluate_traps] retrieved trap: %s" % rule)
        table = RuleTable("Trap rule", mappings, "RegexParser",
             #rawfile,
            "RAWFile",
            None)
        table.addRule(rule)
        
        if settings.DEBUG:  table.dump()
    
        try:
            ctxt = {"service": monitored_service}
            table.evaluate(ctxt)
            logging.info("[evaluate_traps] service: %s has evaluate ALARM" % monitored_service)
            set_indicator(ctxt)
        except Exception, er:
            try:
                logging.debug("[evaluate_traps] threshold has evaluate no alarm, exception: %s" % er)
                monitored_service.alarm_indicators.get().delete()
            except AlarmIndicator.DoesNotExist: pass
            print("No ha cumplido para el servicio: %s" % monitored_service)
            
        
