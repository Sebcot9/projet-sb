# -*- coding:utf-8 -*-
from django import http
from django.shortcuts import render, redirect
from salleblanche.forms import *
from salleblanche.models import *

from django.views.generic import *
from django.contrib import messages 
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import *
import json

# Create your views here.

def login_user(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        login(request, user)
        return redirect('event_list')
    return render(request, 'salleblanche/login.html', locals())


@login_required
def logout_user(request):
    logout(request)
    return redirect('login_user')


class ListEvent(TemplateView):
    model = Events
    template_name = 'salleblanche/eventlist.html'
    context_object_name = 'last_events'
    queryset = Events.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ListEvent, self).get_context_data(**kwargs)
        form = ObjSearchForm(self.request.GET)
        # print get_params
        if self.request.GET:
            context['form'] = form
            self.request.session['bar'] = self.request.GET.get('numobj')
        else:
            context['form'] = form
            self.request.session['bar'] = form.fields['numobj'].choices[0][0]
        return context


def get_object_request(request):
    if request.is_ajax() and request.method == 'POST':
        obj = Objects.objects.filter(category=request.POST.get('category', ''))
        request.session['cat'] = request.POST.get('category', '')
        obj_dict = {}
        for o in obj:
            obj_dict[o.numobject] = o.name
    return http.HttpResponse(json.dumps(obj_dict), content_type='application/json')


# return render(request,'salleblanche/get_object.html', locals())

def get_evt_request(request):
    if request.is_ajax() and request.method == 'POST':
        # print request.POST.get('obj', '')

        request.session['bar'] = request.POST.get('obj', '')
    return redirect('event_list')


class DetailEvent(DetailView):
    model = Events
    template_name = 'salleblanche/eventdetail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(DetailEvent, self).get_context_data(**kwargs)
        context['user'] = Users.objects.get(user=self.request.user.id)
        evt = Events.objects.get(numevent=self.kwargs['pk'])
        context['object'] = Objects.objects.get(numobject=evt.numobject)
        return context

class ListUserEvent(ListView):
	model = Events
	template_name = 'salleblanche/list.html'
	context_object_name = 'events'
	
	def get_queryset(self):
		queryset = Events.objects.filter(numuser = Users.objects.get(user=self.request.user.id).numuser)
		return queryset

class DetailObj(DetailView):
    model = Objects
    template_name = 'salleblanche/objdetail.html'
    context_object_name = 'obj'

    def get_context_data(self, **kwargs):
        context = super(DetailObj, self).get_context_data(**kwargs)
        obj = Objects.objects.get(numobject=self.kwargs['pk'])
        context['category'] = Categories.objects.get(numid=obj.category)
        return context


class CreateEvent(CreateView):
    model = Events
    context_object_name = 'categories'
    template_name = 'salleblanche/eventcreate.html'
    form_class = EventsForm
    success_url = reverse_lazy('event_list')

    def get_form_kwargs(self, **kwargs):
        kwargs = super(CreateEvent, self).get_form_kwargs(**kwargs)
        if self.request.GET:
            kwargs['request'] = self.request.GET
        else:
            kwargs['request'] = self.request.POST       
	return kwargs

    def get_initial(self):
        if self.request.is_ajax():
	    date = self.request.GET.get('date', '')
	    cat = self.request.GET.get('category', '')
	    obj = self.request.GET.get('obj', '')
            # initial = self.request.POST.get('date','')
            # print 
            initial =  	{
			'bookingdate': datetime.strptime(date,'%Y-%m-%d'),
			'category_obj' : cat,
			'numobject': obj,
			'numuser' : self.request.user.id
			}
            return initial

    def form_valid(self, form):
        events = form.save(commit=False)
        userp = Users.objects.get(user=self.request.user.id)
        events.numuser = userp.numuser
        events.numorg = userp.org
        events.registereddate = datetime.now()
        events.lastediteddate = datetime.now()
	messages.success(self.request, "Réservation créée avec succès.\n Une facture vous a été envoyé")
        return super(CreateEvent, self).form_valid(form)


class UpdateEvent(UpdateView):
    model = Events
    template_name = 'salleblanche/event_update.html'
    form_class = EventsForm
    success_url = reverse_lazy('event_list')

    def get_form_kwargs(self, **kwargs):
        kwargs = super(UpdateEvent, self).get_form_kwargs(**kwargs)
        if self.request.GET:
            kwargs['request'] = self.request.GET
        else:
            kwargs['request'] = self.request.POST
        return kwargs

    def form_valid(self, form):
        events = form.save(commit=False)
        userp = Users.objects.get(user=self.request.user.id)
        events.numuser = userp.numuser
        events.numorg = userp.org
        events.lastediteddate = datetime.now()
        return super(UpdateEvent, self).form_valid(form)


class DeleteEvent(DeleteView):
    model = Events
    template_name = 'salleblanche/event_delete.html'
    success_url = reverse_lazy('event_list')


def events_json(request):
    events = Events.objects.filter(numobject=request.session.get('bar'))  # On crée une liste d'evenements
    event_list = []

    for event in events:
        # On récupère les dates dans le bon fuseau horaire
	t = datetime.strptime(event.totime, "%H:%M").time()
	f = datetime.strptime(event.fromtime, "%H:%M").time()
	b = datetime.strptime(event.bookingdate, '%Y-%m-%d')
        event_start = datetime.combine(b, f)
        event_end = datetime.combine(b, t)

        # On décide que si l'événement commence à minuit c'est un
        # événement sur la journée
        if event_start.hour == 0 and event_start.minute == 0:
            allDay = True
        else:
            allDay = False

        if event and event_end > datetime.now():
            event_list.append({
                'id': event.numevent,
                'start': event_start.strftime('%Y-%m-%d %H:%M:%S'),
                'end': event_end.strftime('%Y-%m-%d %H:%M:%S'),
                'title': event_start.strftime('%H:%M') + "-" + event_end.strftime('%H:%M'),
                'startEditable': False,
                'durationEditable': False
            })

    if len(event_list) == -1:
        raise http.Http404
    else:
        return http.HttpResponse(json.dumps(event_list),
                                 content_type='application/json')
