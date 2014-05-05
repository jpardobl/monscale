
class SNMPError(Exception): pass
try:
    import netsnmp
except:
    import pynetsnmp as netsnmp




def get_variable(udp_host, udp_port, community, variable):
    session = netsnmp.Session(DestHost=udp_host, Version=2, Community=community)
    vars = netsnmp.VarList(netsnmp.Varbind(variable) )
    return session.get(vars)
