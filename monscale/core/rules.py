from core.models import METRICS, Threshold, MonitoredService


def evalute():
    
    for machine in MonitoredService.get_monitored_hosts():
        
        table = RuleTable("", mappings, "RegexParser",
             #rawfile,
            "RAWFile",
            None)
        table.setPolicy(False)
        for service in MonitoredService.objects.filter(host=machine, active=True):      
            
            
            
        
            for thres in Rule.objects.filter(active=True, thermostat=True).order_by("pk"):
                table.addRule(rule.to_pypelib())
        
            if settings.DEBUG:
                table.dump()
        
            metaObj = {}
        
            try:
                table.evaluate(metaObj)
            except Exception:
                mappings["tune_to_economic"]()