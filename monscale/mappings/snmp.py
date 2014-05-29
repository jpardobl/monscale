import re, logging

class SNMPError(Exception): pass

try:
    import netsnmp
    snmp_v = 1
except:
    #import pynetsnmp as netsnmp
    try:
        from pysnmp.entity.rfc3413.oneliner import cmdgen
        snmp_v = 2
    except:
        logging.error("Could not load snmp support")




def get_variable(udp_host, udp_port, community, variables):
   
    if snmp_v == 1:
  #      print("snmp_v1")
        session = netsnmp.Session(DestHost=udp_host, Version=2, Community=community)
        vars = netsnmp.VarList(netsnmp.Varbind(variable) )
        return session.get(vars)
    if snmp_v == 2:
 #       print("snmp_v2")
        cg = cmdgen.CommandGenerator()
        comm_data = cmdgen.CommunityData('my-manager', community)
        transport = cmdgen.UdpTransportTarget((udp_host, 161))
         #1.3.6.1.4.1.2021.11.10
#        print variables 
#        if isinstance(variables, str):
#            variables = [x for x in variables.split(".")]
#        variables = (1, 3, 6, 1, 4, 1, 2021, 11, 10, 0)
        errIndication, errStatus, errIndex, result = cg.getCmd(comm_data, transport,variables)
   #      print errIndication,errStatus,errIndex
  #      print "RESULT: %s" % result
        ret = re.search("Integer\((\d+)\)", str(result))
   #     print "RET: %s " % ret.group(1)
        return ret.group(1)

