#!/usr/bin/env python
import os, logging, sys, subprocess
#from django.core.management import call_command

SETTINGS = """
import logging
REDIS_DB = 0
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_ACTION_LIST = "monscale_actions"
REDIS_TRAP_LIST = "monscale_traps"

REDIS_HTTP_REPONSE_TIME_MONITORING_PREFIX = "srvmon_"
ACTION_WORKER_SLEEP_SECS = 10
MONITOR_WORKER_SLEEP_SECS = 10
LOG_LEVEL = logging.DEBUG

#CLOUDFORMS settings
CLOUDFORMS_TEMPLATES   = { "k6"  : " c41ab186-9578-11e3-873d-001a4ae29f48 "}
CLOUDFORMS_API_VERSION = "1.1"
CLOUDFORMS_USERNAME = "admin"
CLOUDFORMS_PASSWORD = "smartvm"
CLOUDFORMS_TEMPLATE_NAME = "k6"
CLOUDFORMS_PXE_IMAGE_ID = "Pxe.Image::3"
CLOUDFORMS_VLAN = "priv1"
INSTALLED_APPS += ('monscale', )
"""

URLS = """
urlpatterns += patterns('',
    url(r'^trap/?', 'monscale.views.trap'),    
)
"""
def deploy(*args, **kwargs): 
    """
    Deploys the Django project and configures it
    """
    logging.basicConfig(level=logging.INFO)
    subprocess.call(["django-admin.py", "startproject", sys.argv[1]])
    os.chdir(sys.argv[1])
    
    with open(os.path.join(sys.argv[1], "settings.py"), "a") as fw: fw.write(SETTINGS)
    with open(os.path.join(sys.argv[1], "urls.py"), "a") as fw: fw.write(URLS)
    
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % sys.argv[1])
    logging.info("[monscale_deploy] Django project %s successfuly created at ./%s" % (sys.argv[1], sys.argv[1]))
    
def evaluate_context(*args, **kwargs):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monscale.settings")

    print os.environ
    #call_command("evaluate_context", sys.argv)