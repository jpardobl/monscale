import simplejson
from monscale.mappings.cloudforms import start_vm, delete_vm
from monscale.mappings.aws import publish_msg_to_sns_topic
from f5 import add_pool_members, del_pool_members

def _load_data(data):
    return simplejson.loads(data)


def launch_cloudforms_vmachine(data):
    """
    data = {
         "cores": ...,
         "megabytes": ...,
         "role": ".....",
         "mtype": "....",
         "os": "....",
         "environment": "....",
         "hostgroup": "....",
         "monitoredservice": "...",
         }
    """
    data = _load_data(data)
    print data
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
    data = {"monitoredservice": "...."}
    """
    data = _load_data(data)
    delete_vm(
        data["monitoredservice"]
        )


def add_f5_pool_members(data):
    """
    f5_host, f5_username, f5_password, pool_name, member_list={}
    data = {
        "f5_host": "...",
        "f5_username": "...",
        "f5_password": "...",
        "pool_name": "...",
        "member_list": ["address:port", ]
    }
    """
    data = _load_data(data)
    add_pool_members(
        data["f5_host"], 
        data["f5_username"], 
        data["f5_password"], 
        data["pool_name"], 
        data["member_list"])

def del_f5_pool_members(data):
    """
    f5_host, f5_username, f5_password, pool_name, member_list={}
    data = {
        "f5_host": "...",
        "f5_username": "...",
        "f5_password": "...",
        "pool_name": "...",
        "member_list": ["address:port", ]
    }
    """
    data = _load_data(data)
    del_pool_members(
        data["f5_host"], 
        data["f5_username"], 
        data["f5_password"], 
        data["pool_name"], 
        data["member_list"])
    
mappings = [
    launch_cloudforms_vmachine,   
    destroy_cloudforms_vmachine,
    add_f5_pool_members,
    del_f5_pool_members,
    publish_msg_to_sns_topic, 
    ]
