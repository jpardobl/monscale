import logging, simplejson, redis
from snmp import get_variable
from django.conf import settings


#logging.basicConfig(level=logging.DEBUG)
def _load_data(data):
    return simplejson.loads(data)



def snmp_oid(ctxt):
    """
    ctxt["service"].data["host"]                  #default: localhost
    ctxt["service"].data["port"]                  #default: 514
    ctxt["service"].data["snmp_read_comunity"]    #default: public
    ctxt["service"].data["snmp_mib"]
    ctxt["service"].data["snmp_variable"]    
    """
    logging.debug("[metric: snmp_oid] Entering  ...")   
    data = _load_data(ctxt["service"].data)
    try:
        ret = get_variable(
            data.get("host", "localhost"), 
            data.get("port", 514),
            data.get("snmp_read_comunity", "public"),
            data["snmp_variable"])
    
    except Exception, er:
        logging.error("[metric: snmp_oid] snmp query ERROR: %s" % er)
        return None
    logging.debug("[metric: snmp_oid] snmp query returned: %s" % ret)
    logging.debug("[metric: snmp_oid] metric ended")
    return ret
    
    
def redis_list_length(ctxt):
    """
    ctxt["service"].data["redis_host"]  #default: localhost
    ctxt["service"].data["redis_port"]  #default: 6379
    ctxt["service"].data["redis_db"]    #default: 0
    ctxt["service"].data["redis_list_name"] 
    """
        
    try:
        #print ctxt["service"].data
        data = _load_data(ctxt["service"].data)
        r = redis.StrictRedis(
            host=data.get("redis_host", "localhost"), 
            port=data.get("redis_port", 6379), 
            db=data.get("redis_db", 0))
        list_length = r.llen(data["redis_list_name"])
    except Exception, er:
        logging.error("[metric: redis_list_length] Exception msg: %s" % er)
        return "[metric: redis_list_length] ERROR trying to rerieve the metric value"
    logging.debug("[metric: redis_list_length] current length: %d" % list_length)
    logging.debug("[metric: redis_list_length] metric ended")
    return list_length


mappings = [
    snmp_oid,
    redis_list_length,
    ]