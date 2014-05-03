from SOAPpy import Config, HTTPTransport, SOAPAddress, WSDL
from django.conf import settings


URL    = 'cfwdsl'

class mytransport(HTTPTransport):
    username = None
    passwd = None
    @classmethod
    def setAuthentication(cls,u,p):
        cls.username = u
        cls.passwd = p
    def call(self, addr, data, namespace, soapaction=None, encoding=None,http_proxy=None, config=Config):
        if not isinstance(addr, SOAPAddress):
            addr=SOAPAddress(addr, config)
        if self.username != None:
            addr.user = self.username+":"+self.passwd
        return HTTPTransport.call(self, addr, data, namespace, soapaction,encoding, http_proxy, config)

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
    mytransport.setAuthentication(settings.CLOUDFORMS_USERNAME, settings.CLOUDFORMS_PASSWORD)
    proxy =  WSDL.Proxy(URL, transport=mytransport)
    print proxy.VmProvisionRequest(
        version=settings.CLOUDFORMS_API_VERSION, 
        templateFields=templateFields, 
        vmFields=vmFields, 
        requester=requester, 
        tags=tags, options=options)
