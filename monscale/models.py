from django.db import models
import simplejson, redis, re, logging
from django.conf import settings
from monscale.mappings import get_mappings


# Create your models here.
ACTIONS = (
    ('launch_cloudforms_vmachine', 'launch_cloudforms_vmachine'),
    ('destroy_cloudforms_vmachine', 'destroy_cloudforms_vmachine'),
    )


class ScaleAction(models.Model):
    name = models.CharField(max_length=100, unique=True)
    action = models.CharField(max_length=100, choices=ACTIONS)
    data = models.TextField()
    
    def __unicode__(self):
        return u"[ScaleAction: %s]" % self.name
    
    def to_dict(self):
        return {
            "type": u"ScaleAction",
            "name": unicode(self.name),
            "action": unicode(self.action),
            "data": simplejson.loads(self.data),
            }  
               
    @staticmethod
    def from_json(data):
        data = simplejson.loads(data)
        a =  ScaleAction(
            name=data["name"],
            action=data["action"],
            data=simplejson.dumps(data["data"]))
        a.save()
        return a
    
    def to_json(self):
        return simplejson.dumps(self.to_dict())
        
    def to_redis(self, justification):
        r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        data = self.to_dict()
        data["justification"] = justification
        dato = simplejson.dumps(data)
        r.lpush(settings.REDIS_ACTION_LIST, dato)
        logging.debug("[ScaleAction.to_redis] %s " % dato)

    def execute(self, justification):
        logging.debug("[ScaleAction.execute] launching action: %s; justification: %s" % 
                      (self.name, justification))
        mappings = get_mappings()
        func = mappings[self.action]
        func(self.data)
        logging.debug("[ScaleAction.execute] finnished")
        ExecutedAction(action=self, justification=justification).save()

       
    @staticmethod
    def from_redis():        
        r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        data = r.rpop(settings.REDIS_ACTION_LIST)
        if data is None: raise ValueError("Action Queue is empty")
                
        logging.debug("[action_worker] retrieved action: %s" % data)
                
        data = simplejson.loads(data)
        try:
            act = ScaleAction.objects.get(name=data["name"])
            return (act, data["justification"])
        except ScaleAction.DoesNotExist as er:
            logging.error("[ScaleAction.from_redis] Action %s came from Redis but not in DB" % data["name"])
            raise er
        
   
    def save(self):
        """
        Need to override to validate json in field data
        """
        try:
            simplejson.loads(self.data)
        except Exception:
            raise AttributeError("Value for data field is not valid json: %s" % self.data)
        super(ScaleAction, self).save()
        
METRICS = (
    ("snmp_oid", "snmp_oid"),
    ("redis_list_length", 'redis_list_length'),
    ("http_response_time", "http_response_time"),
    )

   
OPERANDS = (
    ('>', '>'),
    ('<','<'),
    ('=', '='),
    ('<=', '<='),
    ('>=', '>='),    
    )

class Threshold(models.Model):
    assessment = models.CharField(max_length=255, unique=True)
    time_limit = models.IntegerField() #seconds the threshold must be overtaken before it becomes an alarm
    metric = models.CharField(max_length=100, choices=METRICS) #metric that is going to be monitored. It'll be a mapping.
    operand = models.CharField(max_length=10, choices=OPERANDS)
    value = models.IntegerField() # the value of the threshold
    
    def __unicode__(self):
        return u"[Threshold: %s]" % self.assessment
    
    def to_dict(self):
        return {
            "type": u"Threshold",
            "assessment": unicode(self.assessment),
            "time_limit": self.time_limit,
            "metric": unicode(self.metric),
            "operand": unicode(self.operand),
            "value": self.value, }
        
    def to_json(self):
        return simplejson.dumps(self.to_dict())
    
    @staticmethod
    def from_json(data):
        data = simplejson.loads(data)
        t = Threshold(
            assessment=data["assessment"],
            time_limit=data["time_limit"],
            metric=data["metric"],
            operand=data["operand"],
            value=data["value"]
            )
        t.save()
        return t


class ServiceInfrastructure(models.Model):
    name = models.CharField(max_length=100, unique=True)
    #current_nodes = models.IntegerField(default=0)
    max_nodes = models.IntegerField(default=8) 
    min_nodes = models.IntegerField(default=1)
    
    @property
    def current_nodes(self):
        logging.debug("[ServiceInfrastructure.current_nodes] entering ...")
        from monscale.mappings.cloudforms import get_vms_by_service
        return len(get_vms_by_service(self.name))        
    
    def to_dict(self):
        return {
            "type": u"ServiceInfrastructure",
            "name": self.name,
            "max_nodes": self.max_nodes,
            "min_nodes": self.min_nodes,    
            }
    
    @staticmethod
    def from_json(data):
        data = simplejson.loads(data)
        t = ServiceInfrastructure(
            name=data["name"],
            max_nodes=data["max_nodes"],
            min_nodes=data["min_nodes"]
            )
        t.save()        
        return t       
            
    def __unicode__(self):
        try: 
            num = self.current_nodes
        except:
            num = "ERROR"
        return u"[Infrastructure for service: %s (current nodes: %s)]" % (self.name, num)
    
    
SCALE_TYPE = (
    ('up', 'UP'),
    ('down', 'DOWN'),
    )  


class MonitoredService(models.Model):
    name = models.CharField(max_length=255, unique=True)
    threshold = models.ManyToManyField(Threshold, blank=True)
    action = models.ManyToManyField(ScaleAction, related_name="service")
    active = models.BooleanField(default=True)
    wisdom_time = models.IntegerField(default=120) #secs from last time actions where launch before launching more       
    scale_type = models.CharField(max_length=10, choices=SCALE_TYPE, default='UP')
    infrastructure = models.ForeignKey(ServiceInfrastructure, related_name="services")

    """
    depending on the action, you find here the needed data for that action
    """
    data = models.TextField() 
    
     
    def save(self):
        """
        Need to override to validate json in field data
        """
        try:
            simplejson.loads(self.data)
        except Exception:
            raise AttributeError("Value for data field is not valid json: %s" % self.data)
        super(MonitoredService, self).save()
    
    def to_dict(self):
        return {
            "type": u"MonitoredService",
            "name": unicode(self.name),
            "threshold": [x.assessment for x in self.threshold.all()],
            "action": [x.name for x in self.action.all()],
            "active": self.active,
            "wisdom_time": self.wisdom_time,
            "data": simplejson.loads(self.data),
            "infrastructure": unicode(self.infrastructure.name)}
        
        
        
    def to_json(self):
        return simplejson.dumps(self.to_dict())
    
    @staticmethod
    def from_json(data):
        data = simplejson.loads(data)
     
        ms = MonitoredService(
            name=data["name"],
            active=data["active"],
            wisdom_time=data["wisdom_time"],
            data=simplejson.dumps(data["data"]),
            infrastructure=ServiceInfrastructure.objects.get(name=data["infrastructure"]))
        ms.save()
        for d in data["threshold"]:
            print d
            
        [ms.threshold.add(Threshold.objects.get(assessment=d)) for d in data["threshold"]]
        [ms.action.add(ScaleAction.objects.get(name=d)) for d in data["action"]]
        
        return ms
        
    def to_pypelib(self, value_for_metric=None):       
        out = "if ("
        
        for t in self.threshold.all():
            out += "(%s %s %s) & " % (
                    t.metric if value_for_metric is None else value_for_metric,
                    t.operand,
                    t.value,
                    ) 
        return re.sub("\s&\s$", ") then accept", out)
        
             
    def to_pypelib_prefetched(self, value):
        return simplejson.dumps({
            "obj": {"name": self.name},
            "rule": self.to_pypelib(value)})
    
    def trap_to_redis(self, value):
        r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        r.lpush(settings.REDIS_TRAP_LIST, self.to_pypelib_prefetched(value))

    @staticmethod        
    def from_redis_trap():
        r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        trap = r.rpop(settings.REDIS_TRAP_LIST)
        if trap is None: return (None, None)
        trap = simplejson.loads(trap)
        #print trap
        return (
                MonitoredService.objects.get(name=trap["obj"]["name"]),
                trap["rule"],)                
        
        
    def __unicode__(self):
        return u"[Monitored metric(Escalation %s): %s]" % (self.scale_type, self.name)


class ExecutedAction(models.Model):
    action = models.ForeignKey(ScaleAction)
    timestamp = models.DateTimeField(auto_now_add=True)
    justification = models.TextField()
    
    def __unicode__(self):
        return u"%s - %s, reason: %s" % (self.timestamp, self.action, self.justification)
    
class AlarmIndicator(models.Model):
    service = models.ForeignKey(MonitoredService, related_name='alarm_indicators', unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u"ALARM: %s - %s" % (self.timestamp, self.service)
        

class ActionIndicator(models.Model):
    service = models.ForeignKey(MonitoredService, related_name='action_indicators', unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u"ACTION: %s - %s" % (self.timestamp, self.service)
