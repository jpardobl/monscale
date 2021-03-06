import logging, simplejson, redis, requests, re
from snmp import get_variable
from django.conf import settings
from cloudforms import get_vms_by_service

#logging.basicConfig(level=logging.DEBUG)
def _load_data(data):
    return simplejson.loads(data)


def number_of_nodes(ctxt):
    """
    data = {}
    Uses the monitoredservice Cloudforms tag to retrieve number of nodes
    """
    monitoredservice = ctxt["service"].infrastructure.name

    machines = get_vms_by_service(monitoredservice)
    return len(machines)

def snmp_oid(ctxt):
    """
    ctxt["service"].data["host"]                  #default: localhost
    ctxt["service"].data["port"]                  #default: 514
    ctxt["service"].data["snmp_read_comunity"]    #default: public
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
        logging.debug("[metric: snmp_oid] snmp query for machine: %s returned: %s" % (date.get("host", "localhost"), ret))
        logging.debug("[metric: snmp_oid] metric ended")
        return ret
    except Exception as er:
        logging.debug("[metric: snmp_oid] snmp query ERROR: %s" % er)
        return None


def snmp_oid_service_avg(ctxt):
    """
    REtrieves service infrastructure from ctxt

    data = {
       "snmp_read_comunity": "....",
       "snmp_variable": "...."
    }
    """
    import sys
#    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    try:
        data = _load_data(ctxt["service"].data)

        monitoredservice = ctxt["service"].infrastructure.name

        machines = get_vms_by_service(monitoredservice)
#        print("Returned machines: %s" % machines)
        values = []

        for machine in machines:
            logging.debug("[metric: snmp_oid_service_avg] quering variable %s in machine: %s " % (data["snmp_variable"], machine.name))
            try:
                name = machine.name
                community = data.get("snmp_read_comunity", "public")
                variable = data["snmp_variable"]
                logging.debug("Machine: %s, Community: %s, variable: %s" % (name, community, variable))      
                ret = get_variable(name, 514, community, ".1.3.6.1.4.1.2021.11.9.0")
                logging.debug("[metric: snmp_oid_service_avg] retrieved: %s " % ret)
                values.append(ret)
            except Exception as err:
                logging.error("[metric: snmp_oid_service_avg] reading snmp variable from machine %s got error: %s" % (machine.name, err))

        if not len(values):
            logging.debug("[metric: snmp_oid_service_avg] no values, returning 0")
            return 0

        tot = 0
        for val in values:             
            tot += float(val)
        tot /= len(values)

        logging.debug("[metric: snmp_oid_service_avg] snmp query returned: %s" % tot)
        logging.debug("[metric: snmp_oid_service_avg] metric ended")
        return tot
    except Exception as er:
        logging.error("[metric: snmp_oid_service_avg] Exception: %s" % er)
        return 0



    
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
    except Exception as er:
        logging.error("[metric: redis_list_length] Exception msg: %s" % er)
        return "[metric: redis_list_length] ERROR trying to rerieve the metric value"
    logging.debug("[metric: redis_list_length] current length: %d" % list_length)
    logging.debug("[metric: redis_list_length] metric ended")
    return list_length



def http_content(ctxt):
    """
    ctxt["service"].data = {
       "url": "....",
       "content": "....."
    }
    """
    data = _load_data(ctxt["service"].data)
    ret = requests.get(data["url"])

    logging.debug("[http_content] return: |%s|, type: %s" % (ret.text, type(ret.text)))
    return int(unicode(ret.text) == unicode(data["content"]))


def log4iberia_http_response_time(ctxt):
    """
    ctxt["service"].data["redis_host"]  #default: localhost
    ctxt["service"].data["redis_port"]  #default: 6379
    ctxt["service"].data["redis_db"]    #default: 0

    uses monitoredservice tag to retrieve
    """
    data = _load_data(ctxt["service"].data)
    r = redis.StrictRedis(
        host=data.get("redis_host", "localhost"),
        port=data.get("redis_port", 6379),
        db=data.get("redis_db", 0))

    monitoredservice = "srvmon.%s" % ctxt["service"].infrastructure.name
    logging.debug("[metric: log4iberia_http_response_time] retrieving redis key: %s" % monitoredservice)
    try:
        value = "%0.0f" % float(r.get(monitoredservice))
        r.delete(monitoredservice)
    except Exception as er:
        logging.error("[metric: log4iberia_http_response_time] ERROR retrieving key: %s - %s" % (monitoredservice, er))
        return None
    logging.debug("[metric: log4iberia_http_response_time] retrieved value: %s" % value)
    return value


mappings = [
    number_of_nodes,
    snmp_oid,
    snmp_oid_service_avg,
    redis_list_length,
    http_content,
    log4iberia_http_response_time,
    ]
