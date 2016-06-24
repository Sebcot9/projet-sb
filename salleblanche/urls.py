#-*- coding:utf-8 -*-
from django.conf.urls import include, url
from . import views

urlpatterns = [
    # Examples:
    url(r'^create', views.CreateEvent.as_view(), name='event_create'),
    url(r'^delete/(?P<pk>\d+)$', views.DeleteEvent.as_view(), name='delete'),
    url(r'^update/(?P<pk>\d+)$', views.UpdateEvent.as_view(), name='update'),
    url(r'^list$',views.ListEvent.as_view(), name='event_list'),
    url(r'^myevent$', views.ListUserEvent.as_view(), name='myevents'),
    url(r'^event/(?P<pk>\d+)$',views.DetailEvent.as_view(), name='read_event'),
    url(r'^obj/(?P<pk>\d+)$',views.DetailObj.as_view(), name='read_obj'),
    url(r'^$', views.login_user, name='login_user'),
    url(r'logout', views.logout_user, name='logout_user'),
    url(r'^events.json$', views.events_json, name='events.json'),
    url(r'^get_object$', views.get_object_request, name='obj_request'),
    url(r'^get_event$', views.get_evt_request, name='evt_request')
    ]

