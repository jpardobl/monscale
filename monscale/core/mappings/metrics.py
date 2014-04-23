from django.core.exceptions import ImproperlyConfigured
import logging

def indicator(ctxt):
  
    logging.debug("Entering indicator ...")
    
    logging.debug("ctxt: %s" % ctxt)
    
    logging.debug("Indicator ended")
    

def cpu_usage(ctxt):
  
    logging.debug("Entering cpu_usage metric ...")
    
    logging.debug("ctxt: %s" % ctxt)
    
    logging.debug("cpu_usage metric ended")
    
  
mappings = [
    cpu_usage,   
    ]