from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse
from monscale.models import MonitoredService
import simplejson

def trap(request):
    if request.method != "PUT": 
        return HttpResponseBadRequest(
                content=simplejson.dumps({"errors": "Only PUT method accepted"}),
                content_type="application/json")
    
    try:
        monitoredservice_name = request.POST.get("name")
        monitoredservice_value = request.POST.get("value")
    
        MonitoredService.objects.get(monitoredservice_name).trap_to_redis(monitoredservice_value)
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
        
    