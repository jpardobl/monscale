from django.db import models

# Create your models here.

class ScaleAction(models.Model):
    name = models.CharField(max_length=100)
    scale_by = models.IntegerField() #2 will scal up by two. -2 will scale down by 2
    

   
METRICS = ()
OPERANDS = (
    ('>', '>'),
    ('<','<'),
    ('=', '=='),
    ('<=', '<='),
    ('>=', '>='),    
    )

class Threshold(models.Model):
    assesment = models.CharField(max_length=300)
    time_limit = models.IntegerField() #seconds the threshold must be overtaken before it becomes an alarm
    metric = models.CharField(max_length=100, choices=METRICS) #metric that is going to be monitored. It'll be a mapping.
    operand = models.CharField(max_length=10, choices=OPERANDS)
    value = models.IntegerField() # the value of the threshold
    active = models.BooleanField(default=True)
    
            
class MonitoredService(models.Model):
    name = models.CharField(max_length=300)
    host = models.CharField(max_length=300)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    threshold = models.ForeignKey(Threshold)
    
    @static
    def get_monitored_hosts(self):
        return MonitoredService.objects.filter(active=True).distinct("host")
    
    def to_pypelib(self, ):
        
        with self.threshold as threshold:
            out = "if %s %s %s and indicator " % (
                    threshold.metric, 
                    threshold.operand, 
                    threshold.value)

        return "%s then accept do %s" % (out, self.action)
    
        
        
    class Meta:
        ordering = ["host", ]
    
class AlarmIndicator(models.Model):
    service = models.ForeignKey(MonitoredService)
    timestamp = models.DateTimeField(auto_add_now=True)