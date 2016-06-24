from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'salleb.views.home', name='home'),
    
    url(r'^', include('salleblanche.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
