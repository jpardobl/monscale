import logging, simplejson
from monscale.mappings.cloudforms import start_vm
from monscale.mappings.aws import publish_msg_to_sns_topic


def _load_data(data):
    return simplejson.loads(data)


def launch_cloudforms_vmachine(data):
    """
    data["cores"]
    data["megabytes"]
    data["role"]
    data["mtype"]
    data["os"]
    data["environment"]
    data["hostgroup"]
    """
  #  logging.debug("[launch_cloudforms_vmachine] NOT LAUNCHING:::::::MOCKED:::::::::")
  #  return
    data = _load_data(data)
    start_vm(
        data["cores"],
        data["megabytes"],
        data["role"],
        data["mtype"],
        data["os"],
        data["environment"],
        data["hostgroup"],
        )

def destroy_cloudforms_vmachine(data):
    pass



mappings = [
    launch_cloudforms_vmachine,   
    publish_msg_to_sns_topic, 
    ]