from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor
from django.conf import settings


def start_vm(cores, megabytes, role, mtype, os, environment, hostgroup, name=None):
    template_name = "k6"
    template_guid = settings.CLOUDFORMS_TEMPLATES[template_name]
    mail = 'karim@redhat.com'

    templateFields = "name=%s|request_type=template|guid=%s" % (
        settings.CLOUDFORMS_TEMPLATE_NAME, 
        template_guid)
    #vmFields       = "vm_name=%s|cores_per_socket=%s|memory=%s|vm_memory=%s|vm_auto_start=true|vlan=%s|provision_type=pxe|pxe_image_id=%s" % (
    vmFields       = "cores_per_socket=%s|memory=%s|vm_memory=%s|vm_auto_start=true|vlan=%s|provision_type=pxe|pxe_image_id=%s" % (
        #name, 
        cores, megabytes, megabytes,settings.CLOUDFORMS_VLAN, settings.CLOUDFORMS_PXE_IMAGE_ID)
    requester      = "owner_email=%s|user_name=%s|owner_last_name=User|owner_first_name=Webservice|owner_country=foremanhostgroup/%s;satprofile/%s|owner_office=environment/%s;mtype/%s;operating_system/%s;role/%s" % (
            mail, settings.CLOUDFORMS_USERNAME, hostgroup, hostgroup, environment, mtype, os, role)
    tags          = ''
    options       = ''
    imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
    imp.filter.add('urn:ActionWebService')
    doctor = ImportDoctor(imp)
    proxy = Client(settings.CLOUDFORMS_URL, username=settings.CLOUDFORMS_USERNAME, password=settings.CLOUDFORMS_USERNAME, doctor=doctor)
    print proxy.service.EVMProvisionRequestEx(version='1.1', templateFields=templateFields, vmFields=vmFields, requester=requester, tags=tags, options=options)

