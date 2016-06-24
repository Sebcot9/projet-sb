#-*- coding:utf-8 -*-
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.

from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from datetime import *
from django.core import mail
from decimal import *

class Categories(models.Model):
    numid = models.AutoField(db_column='NumId', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Categories'
    



class Events(models.Model):
    numevent = models.AutoField(db_column='NumEvent', primary_key=True)  # Field name made lowercase.
    numobject = models.IntegerField(db_column='NumObject')  # Field name made lowercase.
    numuser = models.IntegerField(db_column='numUser')  # Field name made lowercase.
    numorg = models.IntegerField(db_column='NumOrg',blank=True, null=True)  # Field name made lowercase.
    numproj = models.IntegerField(db_column='NumProj', blank=True, null=True)  # Field name made lowercase.
    bookingdate = models.DateField(db_column='BookingDate', blank=True, null=True)  # Field name made lowercase.
    fromtime = models.TimeField(db_column='FromTime', blank=True, null=True)  # Field name made lowercase.
    totime = models.TimeField(db_column='ToTime', blank=True, null=True)  # Field name made lowercase.
    comments = models.TextField(db_column='Comments', blank=True, null=True)  # Field name made lowercase.
    participants = models.CharField(db_column='Participants', max_length=100, blank=True, null=True)  # Field name made lowercase.
    registereddate = models.DateTimeField(db_column='RegisteredDate', blank=True, null=True)  # Field name made lowercase.
    lastediteddate = models.DateTimeField(db_column='LastEditedDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Events'

    def save(self, *args, **kwargs):
	super(Events, self).save(*args, **kwargs)
	if self.pk is not None:	
		evt = Events.objects.get(pk = self.pk)		
		facture = Facture.objects.create(event = evt)
		facture.save()
		
	
class Facture(models.Model):
	event = models.OneToOneField(Events)
	cout = models.DecimalField(max_digits=9,decimal_places=2, default=Decimal('0.00'))
	paye = models.BooleanField(default=False)
	
	class Meta:
        	managed = True
        	db_table = 'Facture'
	
	def save(self, *args, **kwargs):
		obj = Objects.objects.get(numobject = self.event.numobject).name
		usermail = Users.objects.get(numuser = self.event.numuser).user.email
		org = Organisations.objects.get(numorg = self.event.numorg)
		if org.acad == 'Y':
			price = Objects.objects.get(numobject = self.event.numobject).priceacad
		else: 
			price = Objects.objects.get(numobject = self.event.numobject).pricenacad
		t = datetime.strptime(self.event.totime, "%H:%M").time()
		f = datetime.strptime(self.event.fromtime, "%H:%M").time()
		b = datetime.strptime(self.event.bookingdate, '%Y-%m-%d')	
		duree = datetime.combine(b,t)-datetime.combine(b,f)
		total_sec = duree.seconds
		sec = total_sec % 60
		total_mins = total_sec/60
		mins = total_mins % 60
		hours = total_mins / 60
		context = Context(prec=2, rounding=ROUND_UP)
		print Decimal(hours)*Decimal(price) + Decimal(price)*Decimal(mins)/Decimal(60)
		self.cout = Decimal(hours)*Decimal(price) + Decimal(price)*Decimal(mins)/Decimal(60)		
		self.paye = False
		subject = 'Reservation de ' + obj
		message =  'Bonjour,\n Vous avez réservé %s pour un total de %d heures et %d minutes. \n Cela vous coutera un total de %8.2f €' % (obj,hours,mins,self.cout)
		from_email = 'seb.cotor@gmail.com'
		to_list = [usermail]
		mail.send_mail(subject, message, from_email, to_list, fail_silently = True ) 
		super(Facture, self).save(*args, **kwargs)

class Objects(models.Model):
    numobject = models.AutoField(db_column='NumObject', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
    category = models.IntegerField(db_column='Category', blank=True, null=True)
    contact = models.CharField(db_column='Contact', max_length=255)  # Field name made lowercase.
    tph = models.CharField(db_column='Tph', max_length=255)  # Field name made lowercase.
    email = models.CharField(db_column='EMail', max_length=255)  # Field name made lowercase.
    participants = models.CharField(db_column='Participants', max_length=100, blank=True, null=True)  # Field name made lowercase.
    accesslevel = models.IntegerField(db_column='AccessLevel', blank=True, null=True)  # Field name made lowercase.
    priceacad = models.DecimalField(db_column='PriceAcad', max_digits=9,decimal_places=2,blank=True, null=True)  # Field name made lowercase.
    pricenacad = models.DecimalField(db_column='PriceNAcad', max_digits=9,decimal_places=2,blank=True, null=True)  # Field name made lowercase.
    image = models.ImageField(db_column='Image', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
   
    class Meta:
        managed = True
        db_table = 'Objects'

    

class Organisations(models.Model):
    numorg = models.AutoField(db_column='numOrg', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=255)  # Field name made lowercase.
    acad = models.CharField(db_column='Acad', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Organisations'


class Projets(models.Model):
    numproj = models.AutoField(db_column='NumProj', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
    numorg = models.CharField(db_column='NumOrg', max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Projets'


class Session(models.Model):
    idsession = models.CharField(db_column='idSession', primary_key=True, max_length=40)  # Field name made lowercase.
    login = models.CharField(max_length=40)
    tempslimite = models.DecimalField(db_column='tempsLimite', max_digits=10, decimal_places=0)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Session'


class Settings(models.Model):
    nom = models.CharField(db_column='Nom', primary_key=True, max_length=100)  # Field name made lowercase.
    valeur = models.CharField(db_column='Valeur', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'Settings'


class Users(models.Model):
    numuser = models.AutoField(db_column='numUser', primary_key=True)  # Field name made lowercase.
    user = models.OneToOneField(User)
    #login = models.CharField(max_length=255)
    #passwd = models.CharField(max_length=255)
    #name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
    #firstname = models.CharField(db_column='FirstName', max_length=255)  # Field name made lowercase.
    org = models.CharField(db_column='Org', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tph = models.CharField(db_column='Tph', max_length=255)  # Field name made lowercase.
    #email = models.CharField(db_column='EMail', max_length=255)  # Field name made lowercase.
    lastobject = models.IntegerField(db_column='LastObject',blank=True, null=True)  # Field name made lowercase.
    accesslevel = models.IntegerField(db_column='AccessLevel', blank=True, null=True)  # Field name made lowercase.
    

    class Meta:
        managed = True
        db_table = 'Users'


class Sessions(models.Model):
    sessionid = models.CharField(primary_key=True, max_length=255)
    login = models.CharField(max_length=255)
    expirationdate = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'sessions'
