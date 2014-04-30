from django.db import models
import simplejson, redis, re, logging
from django.conf import settings

# Create your models here.
ACTIONS = (
    ('launch_cloudforms_vmachine', 'launch_cloudforms_vmachine'),
    ('destroy_cloudforms_vmachine', 'destroy_cloudforms_vmachine'),
    )
class ScaleAction(models.Model):
    name = models.CharField(max_length=100, unique=True)
    action = models.CharField(max_length=100, choices=ACTIONS)
    scale_by = models.IntegerField() #2 will scale up by two. -2 will scale down by 2
    data = models.TextField()
    
    def __unicode__(self):
        return u"%s" % self.name
    
    def to_dict(self):
        return {"name": self.name,
             "scale_by": self.scale_by,}            
        
    def to_redis(self, justification):
        r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        data = self.to_dict()
        data["justification"] = justification
        dato = simplejson.dumps(data)
        r.lpush(settings.REDIS_ACTION_LIST, dato)
        logging.debug("[ScaleAction.to_redis] %s " % dato)
        
    @staticmethod
    def from_redis(data):        
        data = simplejson.loads(data)
        return ScaleAction(name=data["name"], scale_by=["scale_by"])
   
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
    
            
class MonitoredService(models.Model):
    name = models.CharField(max_length=300, unique=True)
    threshold = models.ManyToManyField(Threshold, blank=True)
    action = models.ManyToManyField(ScaleAction)
    active = models.BooleanField(default=True)
    """
    depending on the metric that the monitored service is about, you find here 
    the needed data for that metric
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
    
    def to_json(self):
        return simplejson.dumps({
            "name": self.name,
            })
        
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
    service = models.ForeignKey(MonitoredService, related_name='alarm_indicators')
    timestamp = models.DateTimeField(auto_now_add=True)
    