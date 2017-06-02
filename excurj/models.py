from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
import datetime
from crispy_forms.helper import FormHelper

class City(models.Model):
	city_id = models.CharField(primary_key=True, max_length=150)
	name = models.CharField(max_length=128, blank=True)
	country = models.CharField(max_length=128, blank=True)
	description = models.CharField(max_length=1000, blank=True)
	city_image = models.ImageField(blank=True, upload_to='city_pictures')
	slug = models.SlugField()#MUST MAKE UNIQUE =TRUE AGAIN

	class Meta:
		verbose_name_plural = 'Cities'

	def __str__(self):
		return self.name

	@property
	def photo_url(self):
	    if self.city_image and hasattr(self.city_image, 'url'):
	        return self.city_image.url

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name + " " + self.country)
		super(City, self).save(*args, **kwargs)

	def display_name(self):
		return self.name.split(",")[0]

	display_name = property(display_name)


class Request(models.Model):
	"""traveler requests local to take her out upon liking her profile"""
	traveler = models.ForeignKey(User, related_name='traveler_requests', blank=True)
	local = models.ForeignKey(User, related_name='local_requested', blank=True)
	message = models.CharField(max_length=500)
	date = models.DateField()
	local_approval = models.BooleanField(default=False)

	def __str__(self):
		return self.traveler.first_name + " " + self.local.first_name


class RequestReference(models.Model):
	""" traveler requests local to take her out on an excursion. 
	After they have gone out they leave each other a reference"""

	#Each request gets a reference instance
	request = models.OneToOneField(Request, on_delete=models.CASCADE, primary_key=True)

	traveler_desc = models.CharField(max_length=500, blank=True)#Traveler's reference description
	local_desc = models.CharField(max_length=500, blank=True)

	traveler_fun = models.BooleanField(default=True)#Did the traveler have fun ?
	local_fun = models.BooleanField(default=True)#Did the local have fun ?

	# traveler_date = models.DateField(default=datetime.datetime.now())#When the traveler leave the reference
	# local_date = models.DateField(default=datetime.datetime.now())#When the local leave the reference

	class Meta:
		get_latest_by = "request.id"

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
	user = models.OneToOneField(User, related_name='profile', primary_key=True) #Each User is related to only one User Profile
	city_search_text = models.CharField(blank=True, max_length=300)
	city = models.ForeignKey(City, blank=True, null=True, related_name='city') #Each User Profile must be related to one city.
	prof_pic = models.ImageField(blank=True, upload_to='profile_pictures')
	dob = models.DateField(blank=True, null=True)
	sex = models.CharField(max_length=10, blank=True)
	education = models.CharField(blank=True, max_length=200)
	career = models.CharField(blank=True, max_length=200)
	about_you = models.CharField(max_length=500, blank=True)
	music_movies_books = models.CharField(max_length=200, blank=True)
	friendship = models.CharField(max_length=500, blank=True)
	what_will_you_show_visitors = models.CharField(max_length=1000, blank=True)
	#to add more later

	def __str__(self):
		return self.user.first_name

	def age(self):
		import datetime
		return int((datetime.date.today() - self.dob).days / 365.25  )

	age = property(age)

class Excursion(models.Model):
	"""traveler lists his trips so local could see them and possibly offer to take him out"""
	traveler = models.ForeignKey(User, related_name='traveler_lists_excursion')
	city = models.ForeignKey(City, related_name='visited_city', blank=True, null=True) #Each excursion is connected to one City.
	city_search_text = models.CharField(blank=True, max_length=300)
	message = models.CharField(max_length=500)#message to all locals of that city "Hey good people of Edinburgh!"
	date = models.DateField()

	def __str__(self):
		return self.traveler.first_name.title() + " " + self.traveler.last_name.title() + "'s trip to " + self.city.name + " on " + str(self.date)

class Offer(models.Model):
	""" local offers traveler to take her out based on the trips listed by traveler """
	local = models.ForeignKey(User, related_name='local_offers_excursion')
	message = models.CharField(max_length=500)
	trip = models.ForeignKey(Excursion, related_name='traveler_trip')
	traveler_approval = models.NullBooleanField(default=None)


# class feedback(models.Model):
# 	"""feedback"""
# 	name = models.CharField(max_length=100)
# 	email = models.EmailField()
# 	message = models.CharField(max_length=1500)