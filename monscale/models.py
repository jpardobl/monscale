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
        return u"%s" % self.name
    
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
        
    @staticmethod
    def from_redis(data):        
        data = simplejson.loads(data)
        try:
            act = ScaleAction.objects.get(name=data["name"])
            return (act, data["justification"])
        except ScaleAction.DoesNotExist, er:
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
    assesment = models.CharField(max_length=300, unique=True)
    time_limit = models.IntegerField() #seconds the threshold must be overtaken before it becomes an alarm
    metric = models.CharField(max_length=100, choices=METRICS) #metric that is going to be monitored. It'll be a mapping.
    operand = models.CharField(max_length=10, choices=OPERANDS)
    value = models.IntegerField() # the value of the threshold
    
    def __unicode__(self):
        return u"%s" % self.assesment
    
    def to_dict(self):
        return {
            "type": u"Threshold",
            "assesment": unicode(self.assesment),
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
            assesment=data["assesment"],
            time_limit=data["time_limit"],
            metric=data["metric"],
            operand=data["operand"],
            value=data["value"]
            )
        t.save()
        return t
            
class MonitoredService(models.Model):
    name = models.CharField(max_length=300, unique=True)
    threshold = models.ManyToManyField(Threshold, blank=True)
    action = models.ManyToManyField(ScaleAction)
    active = models.BooleanField(default=True)
    wisdom_time = models.IntegerField(default=120) #secs from last time actions where launch before launching more
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
            "threshold": [x.assesment for x in self.threshold.all()],
            "action": [x.name for x in self.action.all()],
            "active": self.active,
            "wisdom_time": self.wisdom_time,
            "data": simplejson.loads(self.data)}
        
        
        
    def to_json(self):
        return simplejson.dumps(self.to_dict())
    
    @staticmethod
    def from_json(data):
        data = simplejson.loads(data)
     
        ms = MonitoredService(
            name=data["name"],
            active=data["active"],
            wisdom_time=data["wisdom_time"],
            data=simplejson.dumps(data["data"]))
        ms.save()
        for d in data["threshold"]:
            print d
            
        [ms.threshold.add(Threshold.objects.get(assesment=d)) for d in data["threshold"]]
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
        trap = r.lpop(settings.REDIS_TRAP_LIST)
        if trap is None: return (None, None)
        trap = simplejson.loads(trap)
        #print trap
        return (
                MonitoredService.objects.get(name=trap["obj"]["name"]),
                trap["rule"],
                )
                
        
        
    def __unicode__(self):
        return u"if %s" % (self.name)


    
class AlarmIndicator(models.Model):
    service = models.ForeignKey(MonitoredService, related_name='alarm_indicators', unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class ActionIndicator(models.Model):
    service = models.ForeignKey(MonitoredService, related_name='action_indicators', unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    