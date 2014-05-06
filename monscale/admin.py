from django.contrib import admin
from monscale.models import *

class ScaleActionAdmin(admin.ModelAdmin):
    pass
admin.site.register(ScaleAction, ScaleActionAdmin)

class ExecutedActionAdmin(admin.ModelAdmin):
    pass
admin.site.register(ExecutedAction, ExecutedActionAdmin)

class ThresholdAdmin(admin.ModelAdmin):
    pass
admin.site.register(Threshold, ThresholdAdmin)

class MonitoredServiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(MonitoredService, MonitoredServiceAdmin)

class AlarmIndicatorAdmin(admin.ModelAdmin):
    pass
admin.site.register(AlarmIndicator, AlarmIndicatorAdmin)

class ActionIndicatorAdmin(admin.ModelAdmin):
    pass
admin.site.register(ActionIndicator, ActionIndicatorAdmin)