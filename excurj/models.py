from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
import datetime
from crispy_forms.helper import FormHelper
from django.contrib.sitemaps import ping_google



class City(models.Model):
	"""
	Each user must associated with a City.

	City ID is pulled from the Google Places API

	City Image, lat and lng are also pulled from the same API

	Description is pulled from the Wikipedia API

	"""
	city_id = models.CharField(primary_key=True, max_length=150)
	name = models.CharField(max_length=128, blank=True)
	country = models.CharField(max_length=128, blank=True)
	description = models.CharField(max_length=1000, blank=True)
	city_image = models.ImageField(blank=True, upload_to='city_pictures')
	slug = models.SlugField()#MUST MAKE UNIQUE =TRUE AGAIN
	lat = models.FloatField(blank=True, null=True)
	lng = models.FloatField(blank=True, null=True)

	class Meta:
		verbose_name_plural = 'Cities'

	def __str__(self):
		return self.name

	@property
	def photo_url(self):
	    if self.city_image and hasattr(self.city_image, 'url'):
	        return self.city_image.url

	#Override save to save city name as a slug
	def save(self, *args, **kwargs):
		self.slug = slugify(self.name + " " + self.country)
		super(City, self).save(*args, **kwargs)
		try:
			ping_google()
		except Exception:
		# Bare 'except' because we could get a variety
		# of HTTP-related exceptions.
			pass

	#Display name pulls the city name without province/state/country 
	#for ex: New York, New York, USA becomes New York
	def display_name(self):
		return self.name.split(",")[0]

	display_name = property(display_name)


	def get_absolute_url(self):
		return 'city/%s/' % self.slug


class Request(models.Model):
	"""traveler requests local to take her out upon liking her profile"""
	traveler = models.ForeignKey(User, related_name='traveler_requests', blank=True)
	local = models.ForeignKey(User, related_name='local_requested', blank=True)
	message = models.CharField(max_length=500)
	date = models.DateField()
	local_approval = models.NullBooleanField(default=None, null=True)

	class Meta:
		get_latest_by = "id"

	def __str__(self):
		return self.traveler.first_name + " " + self.local.first_name


class RequestReference(models.Model):
	""" traveler requests local to take her out on an excursion. 
	After they have gone out they leave each other a reference
	"""

	#Each request gets a reference instance
	request = models.OneToOneField(Request, on_delete=models.CASCADE, primary_key=True,\
	 related_name='reference_request')

	#traveler and local description
	traveler_desc = models.CharField(max_length=500, blank=True)#Traveler's reference description
	local_desc = models.CharField(max_length=500, blank=True)

	#Did the traveler have fun with the local? and the other way around?
	#if they both enjoyed the outing/excursion their reference is featured on the front page
	traveler_fun = models.BooleanField(default=True)#Did the traveler have fun ?
	local_fun = models.BooleanField(default=True)#Did the local have fun ?

	# traveler_date = models.DateField(default=datetime.datetime.now())#When the traveler leave the reference
	# local_date = models.DateField(default=datetime.datetime.now())#When the local leave the reference

	class Meta:
		get_latest_by = "request_id"

	def __str__(self):
		return self.traveler_desc	

# class OfferReference(models.Model):
# 	""" Local offers traveler to take her out. 
# 	For ex: I'm in London and a person is coming to London soon, then I offer to take her out
# 	After they have met, they leave a reference for each other """

# 	#Each offer gets a reference instance
# 	offer = models.OneToOneField(Offer, on_delete=models.CASCADE, primary_key=True)

# 	traveler_desc = models.CharField(max_length=500, blank=True)#Traveler's reference description
# 	local_desc = models.CharField(max_length=500, blank=True)

# 	traveler_fun = models.BooleanField()#Did the traveler have fun ?
# 	local_fun = models.BooleanField()#Did the local have fun ?

# 	# traveler_date = models.DateField(default=datetime.datetime.now())#When the traveler leave the reference
# 	# local_date = models.DateField(default=datetime.datetime.now())#When the local leave the reference

# 	class Meta:
# 		get_latest_by = "request.id"

# 	def __str__(self):
# 		return self.description	



class UserProfile(models.Model):
	"""Each User instance is associated with a profile instance - One to One"""

	#Each User is related to only one User Profile
	user = models.OneToOneField(User, related_name='profile', primary_key=True)

	#User picks city from the autocomplete, then the text is used to pull or create a city 
	city_search_text = models.CharField(blank=True, max_length=300)
	city = models.ForeignKey(City, blank=True, null=True, related_name='city') #Each User Profile must be related to one city.
	prof_pic = models.ImageField(blank=True, upload_to='profile_pictures')
	dob = models.DateField(blank=True, null=True)
	sex = models.CharField(max_length=10, blank=True)
	education = models.CharField(blank=True, max_length=200)
	career = models.CharField(blank=True, max_length=200)
	about_you = models.CharField(max_length=500, blank=True)
	music_movies_books = models.CharField(max_length=1000, blank=True)

	#What is the user's view on forming friendships via travel instead of the typical tourist experience
	friendship = models.CharField(max_length=500, blank=True)

	what_will_you_show_visitors = models.CharField(max_length=1000, blank=True)
	#to add more later

	def __str__(self):
		return self.user.first_name

	def age(self):
		import datetime
		return int((datetime.date.today() - self.dob).days / 365.25  )

	age = property(age)

		#Override save to ping google
	def save(self, *args, **kwargs):
		super(UserProfile, self).save(*args, **kwargs)
		try:
			ping_google()
		except Exception:
		# Bare 'except' because we could get a variety
		# of HTTP-related exceptions.
			pass

	def get_absolute_url(self):
		return 'user/%s/' % self.user.username

class Excursion(models.Model):
	"""
		Traveler lists his trips so locals could see her and possibly offer to take her out
		The term Excursion, outing and trip are used interchangeabily across the app

	"""
	traveler = models.ForeignKey(User, related_name='traveler_lists_excursion')
	local = models.ForeignKey(User, related_name='local_who_offered', blank=True, null=True)
	city = models.ForeignKey(City, related_name='visited_city', blank=True, null=True) #Each excursion is connected to one City.
	city_search_text = models.CharField(blank=True, max_length=300)
	message = models.CharField(max_length=500)#message to all locals of that city "Hey good people of Edinburgh!"
	date = models.DateField()

	def __str__(self):
		return self.traveler.first_name.title() + " " + self.traveler.last_name.title() + "'s trip to " + self.city.name + " on " + str(self.date)

	#Override save to ping google
	def save(self, *args, **kwargs):
		super(Excursion, self).save(*args, **kwargs)
		try:
			ping_google()
		except Exception:
		# Bare 'except' because we could get a variety
		# of HTTP-related exceptions.
			pass


	def get_absolute_url(self):
		return 'user/%s/#trips' % self.traveler.username

class Offer(models.Model):
	""" local offers traveler to take her out based on the trips listed by traveler """
	local = models.ForeignKey(User, related_name='local_offers_excursion')
	message = models.CharField(max_length=500)
	trip = models.ForeignKey(Excursion, related_name='traveler_trip')
	traveler_approval = models.NullBooleanField(default=None)
	def __str__(self):
		return trip.id


# class feedback(models.Model):
# 	"""feedback"""
# 	name = models.CharField(max_length=100)
# 	email = models.EmailField()
# 	message = models.CharField(max_length=1500)