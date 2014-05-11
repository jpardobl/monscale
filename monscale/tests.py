from django.test import TestCase
from models import *
# Create your tests here.
from django.conf import settings
from monscale.mappings.metrics import *
from monscale.mappings.snmp import get_variable
from monscale.mappings.actions import launch_cloudforms_vmachine, destroy_cloudforms_vmachine
from monscale.mappings.cloudforms import get_vms_by_service
import logging

SNMP_HOST = "172.21.229.225"
SNMP_PORT = 161
SNMP_COMMUNITY = "net1000"

#logging.disable(logging.CRITICAL)

class SOAPTest(TestCase):

    def test_nums(self):
        print len(get_vms_by_service("logstash"))
 
    def test_create(self):
	launch_cloudforms_vmachine('{"cores": 1, "megabytes": 1024, "role": "ut", "mtype": "grid", "os": "l", "environment": "lab", "hostgroup": "indexer","monitoredservice": "logstash" }')

    def setUp2(self):

        ScaleAction(name="prueba", action="launch_cloudforms_vmachine", data='{"environment": "lab", "hostgroup": "indexer", "mtype": "grid", "role": "ut", "megabytes": 1024, "cores": 1, "os": "l", "monitoredservice": "logstash"}').save()
    def test_create2(self):
        self.setUp2()         
        a = ScaleAction.objects.get()
        a.to_redis("pruba")
        action, jutification = ScaleAction.from_redis()
        action.execute(jutification)        

    def test_delete(self):
        destroy_cloudforms_vmachine('{"monitoredservice": "logstash"}')

class MetricTest(TestCase):
    def setUp(self):
        pass
    
    def test_snmp(self):
        print(get_variable(SNMP_HOST, SNMP_PORT, SNMP_COMMUNITY, ".1.3.6.1.4.1.2021.11.9.0"))
    

class F5Test(TestCase):
    
    def test_add_member(self):
        from monscale.mappings.actions import add_f5_pool_members
        
        add_f5_pool_members('{"f5_host": "172.21.200.49","f5_username": "admin", "f5_password": "lab5000", "pool_name": "pepito","member_list": ["172.21.200.184:80"]}')

    def test_del_member(self):
        from monscale.mappings.actions import add_f5_pool_members, del_f5_pool_members
        
        del_f5_pool_members('{"f5_host": "172.21.200.49","f5_username": "admin", "f5_password": "lab5000", "pool_name": "pepito","member_list": ["172.21.200.184:80"]}')
    
        
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
    
    def off_test_1(self):
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
    def off_test_2(self):
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
            
