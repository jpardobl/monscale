from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^trap/?', 'monscale.views.trap'),    
)