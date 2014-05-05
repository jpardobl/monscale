import simplejson
from monscale.mappings.cloudforms import start_vm, delete_vm
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
    data["monitoredservice"]
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
        data["monitoredservice"]
        )

def destroy_cloudforms_vmachine(data):
    """
    data["monitoredservice"]
    """
    data = _load_data(data)
    delete_vm(
        data["monitoredservice"]
        )

mappings = [
    launch_cloudforms_vmachine,   
    destroy_cloudforms_vmachine,
    publish_msg_to_sns_topic, 
    ]
