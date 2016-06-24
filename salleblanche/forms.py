#-*- coding:utf-8 -*-
from django import forms
from models import *
from widgets import SplitTimeWidget , SplitTimeField
from django.forms import extras
from datetime import *

class ObjSearchForm(forms.Form):

	category_obj = forms.ChoiceField(choices = [(c[0], '%s'%c[1])
	for c in Categories.objects.values_list('numid','name')],label='Categories', widget=forms.Select(attrs={"onChange":'get_object();'}))

	numobj = forms.ChoiceField(choices = [(o[0], '%s'%o[1])
	for o in Objects.objects.values_list('numobject','name')],label='Objet à réserver',widget=forms.Select(attrs={
                                   "onChange":'get_event();'}))

	def __init__(self, request, *args, **kwargs):
		self.request = request
		super(ObjSearchForm, self).__init__(*args, **kwargs)
		obj = {}
		choice_list = []
		if request :
			obj = Objects.objects.filter(category=request.get('category_obj', ''))
			for o in obj:
				choice_list.append((o.numobject,o.name))
		else:
			obj = Objects.objects.filter(category = self.fields['category_obj'].choices[0][0])
			for o in obj:
				choice_list.append((o.numobject,o.name))
		super(ObjSearchForm, self).__init__(*args, **kwargs)
		self.fields['category_obj'].initial = request.get('category_obj')
		self.fields['numobj'] = forms.ChoiceField(choices = choice_list, widget=forms.Select(attrs={"onChange":'get_event();'}),initial = request.get('numobj') ,label='Objet à réserver')

#Formulaire d'evenements
class EventsForm(forms.ModelForm):
	numuser = forms.IntegerField()
	category = forms.ChoiceField(choices=[(c[0], '%s' % c[1])
											  for c in Categories.objects.values_list('numid', 'name')],
									 label='Categories', widget=forms.Select(attrs = {"onChange":'filt_object();'}))

	numobject = forms.ChoiceField(choices = [(o[0], '%s'%(o[1]))
	for o in Objects.objects.values_list('numobject','name')],label='Objet à réserver')

	numproj = forms.ModelChoiceField(queryset= (Projets.objects.values_list('numproj','name')),label="Pour le projet", empty_label="(Aucun projet)", required=False)
	bookingdate = forms.DateField(widget=extras.SelectDateWidget(attrs={'class':'large-2 medium-2 small-2 columns end'}),label='Date de réservation', initial=datetime.today()+timedelta(days=1))
	fromtime = SplitTimeField(widget=SplitTimeWidget(attrs={'class':'large-1  medium-2 small-3 columns end'}),label='De :')
	totime = SplitTimeField(widget=SplitTimeWidget(attrs={'class':'large-1  medium-2 small-3 columns end'}),label='À :')
	comments = forms.CharField(widget = forms.Textarea(),label='Commentaires', required=False)
	participants = forms.CharField(initial='1')
	class Meta:
		model = Events
		fields = ('numuser','category','numobject','bookingdate','fromtime','totime','comments','participants','numproj')

	def __init__(self, request=None, *args, **kwargs):
		super(EventsForm, self).__init__(*args, **kwargs)
		self.request = request
		obj = {}
		choice_list = []
		if request :
			obj = Objects.objects.filter(category=request.get('category', ''))
			for o in obj:
				choice_list.append((o.numobject,o.name))
		else:
			obj = Objects.objects.filter(category=self.fields['category'].choices[0][0])
			for o in obj:
				choice_list.append((o.numobject, o.name))
		super(EventsForm, self).__init__(*args, **kwargs)
		self.fields['category'].initial = request.get('category')
		self.fields['numobject'] = forms.ChoiceField(choices = choice_list, widget=forms.Select(),label = 'Objet à réserver' ,initial =request.get('numobj'))
	
	def clean(self):
		if self:
			
			cleaned_data = super(EventsForm, self).clean()
			errors = []
			user = Users.objects.get(user=cleaned_data.get("numuser"))
			numobject = cleaned_data.get("numobject")
			fromtime = cleaned_data.get("fromtime")
			totime = cleaned_data.get("totime")
			bookingdate = cleaned_data.get("bookingdate")
			
			objet = Objects.objects.get(numobject = numobject)		
			evt = Events.objects.filter(numobject = numobject).all()
			
			eventdate = evt.filter(bookingdate=bookingdate)
			overlap = eventdate.filter(fromtime__lt=totime,totime__gt=fromtime) #http://stackoverflow.com/questions/325933/determine-whether-two-date-ranges-overlap

			if user.accesslevel < objet.accesslevel:
				errors.append(forms.ValidationError("Votre niveau d'accès est trop bas, veuillez contacter le gestionnaire de l'objet"))

			if bookingdate <= date.today():
				errors.append(forms.ValidationError("La date de début doit être strictement postérieure à la date actuelle"))

			if overlap : #Si les dates se chevauchent
				errors.append(forms.ValidationError("L'objet demandé n'est pas disponible, veuillez choisir une autre plage horaire !"))

			if fromtime >= totime:
				errors.append(forms.ValidationError("La date de début doit être strictement antérieur à celle de fin"))

			if errors:
				raise forms.ValidationError(errors)
			return cleaned_data
		
