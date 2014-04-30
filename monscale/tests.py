from django.test import TestCase
from models import *
# Create your tests here.
from django.conf import settings


class TrapTest(TestCase):
    
    def setUp(self):
        for ms in MonitoredService.objects.all(): ms.delete()
        for o in ScaleAction.objects.all(): o.delete()
        for o in Threshold.objects.all(): o.delete()
        for o in AlarmIndicator.objects.all(): o.delete()
        self.redis = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        self.redis.delete(settings.REDIS_TRAP_LIST)
        
    def setup_1(self):
        a = ScaleAction(
            name="scale_by1",
            action="launch_cloudforms_vmachine",
            scale_by=1,
            data="{}",
            )
        a.save()
        t = Threshold(
            assesment="a1",
            time_limit=10,
            metric="redis_list_length",
            operand=">",
            value=50,
            )
        t.save()
        ms = MonitoredService(
            name="name1",

            active=True,
            data="{}",
            )
        
        ms.save()
        ms.threshold.add(t)
        ms.action.add(a)

        return (a, t, ms)
    
    def setup_2(self):
        a = ScaleAction(
            name="scale_by1",
            action="launch_cloudforms_vmachine",
            scale_by=1,
            data="{}",
            )
        a.save()
        t = Threshold(
            assesment="a1",
            time_limit=10,
            metric="redis_list_length",
            operand=">",
            value=50,
            )
        t.save()
        a2 = ScaleAction(
            name="scale_by2",
            action="launch_cloudforms_vmachine",
            scale_by=1,
            data="{}",
            )
        a2.save()
        t2 = Threshold(
            assesment="a2",
            time_limit=10,
            metric="redis_list_length",
            operand=">",
            value=70,
            )
        t2.save()
        ms = MonitoredService(
            name="name1",
            active=True,
            data="{}",
            )
        
        ms.save()
        ms.threshold.add(t)
        ms.action.add(a)
        ms.threshold.add(t2)
        ms.action.add(a2)
        #print "TO PYPELIB: %s" % ms.to_pypelib()
        return (a, t, ms)
    
    def test_1(self):
        a, t, ms = self.setup_1()        

        ms.trap_to_redis(40)
        
        self.assertEqual(1,
             self.redis.llen(settings.REDIS_TRAP_LIST),
            "Not properly persisting traps in redis",
            )
        
        mss, rule = MonitoredService.from_redis_trap()
        
        self.assertIsInstance(mss, MonitoredService, "Not properly retrieving traps from redis")
        self.assertEqual(mss.id,ms.id, "Not properly retrieving traps from redis")
        self.assertIsInstance(rule, str, "Not properly retrieving traps from redis")
    def test_2(self):
        a, t, ms = self.setup_2()        

        ms.trap_to_redis(40)
        
        self.assertEqual(1,
             self.redis.llen(settings.REDIS_TRAP_LIST),
            "Not properly persisting traps in redis",
            )
        
        mss, rule = MonitoredService.from_redis_trap()
        
        self.assertIsInstance(mss, MonitoredService, "Not properly retrieving traps from redis")
        self.assertEqual(mss.id,ms.id, "Not properly retrieving traps from redis")
        self.assertIsInstance(rule, str, "Not properly retrieving traps from redis")
            