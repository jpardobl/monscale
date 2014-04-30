from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
from monscale.models import MonitoredService
import simplejson
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import QueryDict

@csrf_exempt
def trap(request):
    if request.method != "PUT": 
        return HttpResponseBadRequest(
                content=simplejson.dumps({"errors": "Only PUT method accepted"}),
                content_type="application/json")
    
    try:
        print("[views.trap] entering ...")
        params = QueryDict(request.body, request.encoding)
        monitoredservice_name = params["name"]
        monitoredservice_value = params["value"]
        
        print("[views.trap] monitored service: %s, new value: %s" % (monitoredservice_name, monitoredservice_value))
        
        MonitoredService.objects.get(name=monitoredservice_name).trap_to_redis(monitoredservice_value)
        response = HttpResponse("Metric updated")
        response.status_code = 204
        response['Cache-Control'] = 'no-cache'
        return response
    
    except MonitoredService.DoesNotExist:
        return HttpResponseNotFound(
                content=simplejson.dumps({"errors": "No MonitoredService found undr name: %s" % monitoredservice_name}),
                content_type="application/json",)
        
    except Exception, er:
        return HttpResponseBadRequest(
                content=simplejson.dumps({"errors": str(er)}),
                content_type="application/json")
        
    