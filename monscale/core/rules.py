from core.models import METRICS, Threshold, MonitoredService
from core.mappings import get_mappings
from pypelib.RuleTable import RuleTable
import logging
from django.conf import settings


def evaluate():
    
    for machine in MonitoredService.get_monitored_hosts():
        mappings = get_mappings()
        table = RuleTable("", mappings, "RegexParser",
             #rawfile,
            "RAWFile",
            None)
        table.setPolicy(False)
        for service in MonitoredService.objects.filter(host=machine, active=True):      
                table.addRule(service.to_pypelib())
        
        if settings.DEBUG:
            table.dump()
        try:
            table.evaluate({"machine": machine})
        except Exception:
            print("no ha cumplido para la maquina: %s" % machine)