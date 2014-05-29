from monscale.models import ServiceInfrastructure
from monscale.mappings.actions import add_f5_pool_members, del_f5_pool_members
from monscale.mappings.f5 import get_pool_members
from monscale.mappings.cloudforms import get_vms_by_service
import logging, simplejson
import socket
from django.conf import settings
#>>> socket.gethostbyname('google.com')

logger = logging.getLogger("loadbalancer")
logger.setLevel(settings.LOG_LEVEL)


def synclb():
    """
    Retrieves the machines by monitoredservice tag from CloudForms and ensures that they
    exists as load balancer pool nodes
    """

    for infrastructure in ServiceInfrastructure.objects.filter(loadbalanced=True):
        good_nodes = ["%s:%s" % (socket.gethostbyname(x.name), infrastructure.loadbalancer_node_port) for x in get_vms_by_service(infrastructure.name)]
        lb_nodes = get_pool_members(
            infrastructure.loadbalancer_host,
            infrastructure.loadbalancer_username,
            infrastructure.loadbalancer_password,
            infrastructure.fqdn)

        struc = {
            "f5_host": infrastructure.loadbalancer_host,
            "f5_username": infrastructure.loadbalancer_username,
            "f5_password": infrastructure.loadbalancer_password,
            "pool_name": infrastructure.fqdn,
            "member_list": good_nodes
        }


        add_f5_pool_members(simplejson.dumps(struc))
        bad_nodes = [item for item in lb_nodes if item not in good_nodes]

        logger.debug("[synclb] loadbalancer nodes: %s" % lb_nodes)
        logger.debug("[synclb] nodes in cloudforms: %s" % good_nodes)
        logger.debug("[synclb] node to drop from lb pool: %s" % bad_nodes)

        if not len(bad_nodes):
            return
        struc["member_list"] = bad_nodes
        del_f5_pool_members(simplejson.dumps(struc))







