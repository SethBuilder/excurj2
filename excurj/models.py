from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

class City(models.Model):
	city_id = models.CharField(primary_key=True, max_length=150)
	name = models.CharField(max_length=128)
	country = models.CharField(max_length=128)
	description = models.CharField(max_length=1000, blank=True)
	city_image = models.ImageField(blank=True, upload_to='city_pictures')

	class Meta:
		verbose_name_plural = 'Cities'

	def __str__(self):
		return self.name

class Reference(models.Model):
	author = models.ForeignKey(User, related_name='referencer')#can be local or traveler
	referenced = models.ForeignKey(User, related_name='referencee')#can be local or traveler
	description = models.CharField(max_length=500)
	fun = models.BooleanField() #did you have fun with the person or not?
	

class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name='profile') #Each User is related to only one User Profile
	city = models.ForeignKey(City) #Each User Profile must be related to one city.
	prof_pic = models.ImageField(blank=True, upload_to='profile_pictures')
	dob = models.DateField()
	sex = models.CharField(max_length=50, blank=True)
	about_you = models.CharField(max_length=500, blank=True)
	music_movies_books = models.CharField(max_length=200, blank=True)
	career = models.CharField(blank=True, max_length=200)
	education = models.CharField(blank=True, max_length=200)
	what_will_you_show_visitors = models.CharField(max_length=1000)
	#to add more later

class Request(models.Model):
	"""traveler requests local to take him out upon liking his profile"""
	traveler = models.ForeignKey(User, related_name='traveler_requests')
	local = models.ForeignKey(User, related_name='local_requested')
	message = models.CharField(max_length=500)
	date = models.DateField()
	local_approval = models.BooleanField(blank=True)

class Excursion(models.Model):
	"""traveler lists his trips so local could see them and possibly offer to take him out"""
	traveler = models.ForeignKey(User, related_name='traveler_lists_excursion')
	message = models.CharField(max_length=500)
	date = models.DateField()

class Offer(models.Model):
	""" local offers traveler to take out based on the trips listed by traveler """
	traveler = models.ForeignKey(User, related_name='traveler_receives_offer')
	local = models.ForeignKey(User, related_name='local_offers_excursion')
	message = models.CharField(max_length=500)
	trip = models.ForeignKey(Excursion)
	traveler_approval = models.BooleanField(blank=True)
