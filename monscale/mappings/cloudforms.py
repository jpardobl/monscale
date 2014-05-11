from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor
from django.conf import settings
import logging

API_VERSION = "1.1"
#logging.disable(logging.CRITICAL)

def cloudforms_connect():
    imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
    imp.filter.add('urn:ActionWebService')
    doctor = ImportDoctor(imp)
    logging.disable(logging.CRITICAL)
    proxy = Client(settings.CLOUDFORMS_URL, username=settings.CLOUDFORMS_USERNAME, password=settings.CLOUDFORMS_PASSWORD, doctor=doctor)
    logging.basicConfig(level=settings.LOG_LEVEL)
    return proxy
    
def start_vm(cores, megabytes, role, mtype, os, environment, hostgroup, monitoredservice, name=None):
    template_name = "k6"
    template_guid = settings.CLOUDFORMS_TEMPLATES[template_name]
    mail = 'karim@redhat.com'

    templateFields = "name=%s|request_type=template|guid=%s" % (
        settings.CLOUDFORMS_TEMPLATE_NAME, 
        template_guid)
    vmFields       = "vm_name=%s|cores_per_socket=%s|memory=%s|vm_memory=%s|vm_auto_start=true|vlan=%s|provision_type=pxe|pxe_image_id=%s" % (
        name, 
        cores, megabytes, megabytes,settings.CLOUDFORMS_VLAN, settings.CLOUDFORMS_PXE_IMAGE_ID)
    requester      = "owner_email=%s|user_name=%s|owner_last_name=User|owner_first_name=Webservice|owner_country=foremanhostgroup/%s;satprofile/%s;monitoredservice/%s|owner_office=environment/%s;mtype/%s;operating_system/%s;role/%s" % (
            mail, settings.CLOUDFORMS_USERNAME, hostgroup, hostgroup, monitoredservice, environment, mtype, os, role )
    #print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&: %s" % requester)
    tags          = ''
    options       = ''
    proxy = cloudforms_connect()
    print proxy.service.EVMProvisionRequestEx(version=API_VERSION, templateFields=templateFields, vmFields=vmFields, requester=requester, tags=tags, options=options)
	

def delete_vm(monitoredservice):
    mail           = 'karim@redhat.com'
    uri_parts      = "namespace=Karim/RedHat|class=Misc|instance=retire|message=create"
    requester      = "user_name=%s|auto_approve=true|owner_email=%s" % (settings.CLOUDFORMS_USERNAME, mail)
    proxy = cloudforms_connect()
    vms = get_vms_by_service(monitoredservice)
    vmname, vmid = None, None
    for vm in vms:
        if vm.retired != True:
            vmname, vmid = vm.name, vm.id
            break
    #print vmname, vmid
    if vmid:
        parameters       = "vmid=%s|request_type=vm_retired" % (vmid)
        print proxy.service.CreateAutomationRequest(version=API_VERSION, uri_parts=uri_parts, parameters=parameters, requester=requester )

def get_vms_by_service(monitoredservice):
    
    proxy = cloudforms_connect()
    return proxy.service.GetVmsByTag("monitoredservice/%s" % monitoredservice )
    
