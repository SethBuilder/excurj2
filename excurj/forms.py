from django import forms
from django.contrib.auth.models import User
from excurj.models import UserProfile, City, Request, Excursion, Offer, RequestReference
from django.db import models
import datetime

#Displayed on the UserProfileForm
class UserForm(forms.ModelForm):

	#FIRST NAME
	first_name = forms.CharField(
		label = "First Name:",
		max_length = 80,
		required = True
		)
	#LAST NAME
	last_name = forms.CharField(
		label = "Last Name:",
		max_length = 80,
		required = True,
		)

	#ONLY DISPLAY FIRST/LAST NAME
	class Meta:
	    model = User
	    fields = ('first_name', 'last_name')



#Edit User account
class EditAccountForm(forms.ModelForm):
	class Meta:

		#ONLY EDIT FIRST/LAST NAME, USERNAME, EMAIL ADDRESS
		model = User
		exclude = ('password','is_staff', 'is_active', 'user_permissions', 'groups', 
			'date_joined', 'last_login', 'date_joined', 'is_superuser')



#USED TO ENSURE USERS ARE 13 YEARS AND OLDER
def get_current_year():
	now = datetime.datetime.now() 
	return now.year

_13_or_older = get_current_year() -13


#Create UserProfile
class UserProfileForm(forms.ModelForm):

	city_search_text = forms.CharField(
		label = "Your Current City",
		max_length = 200,
		required = True,
		)

	prof_pic = forms.ImageField(
		label = "Your Profile Picture",
		required = False
		)

	dob = forms.DateField(
		widget=forms.SelectDateWidget(years=range(1930, _13_or_older )),
		label = "Your Birthday",
		required = True,
		initial = datetime.date(1980,1,1)
		)

	music_movies_books = forms.CharField(
		widget=forms.Textarea(),
		label = "Music, Movies and Books You Like",
		max_length = 2000,
		required = False,
		)

	friendship = forms.CharField(
		widget = forms.Textarea(),
		label = "What is your view on forming frienships via travel" 
		"as an alternative to the typical tourist experince?",
		required=False,
		max_length=
		2000,
		)

	what_will_you_show_visitors = forms.CharField(
		label = "What will you show visitors in your town?",
		required = True,
		widget=forms.Textarea(),
		max_length=5000
		)

	"""Exclude city as it'll be pulled from database or create it if it doesn't exist 
	   	based on the searched text from Google Autocomplete API

	   EXCLUDE USER AS IT IS PASSED THRU REQUEST"""
	class Meta:
	    model = UserProfile
	    exclude = ('city','user')
	    # fields = ('city_search_text','city','prof_pic', 'dob', 'sex', 'education', 'career', 'about_you', 
	    # 	'music_movies_books','friendship','what_will_you_show_visitors', )



#Edit profile
class EditProfileForm(forms.ModelForm):

	city_search_text = forms.CharField(
		label = "Your Current City",
		max_length = 200,
		required = True,
		)

	prof_pic = forms.ImageField(
		label = "Your Profile Picture",
		required=False,
		)

	dob = forms.DateField(
		widget=forms.SelectDateWidget(years=range(1930, _13_or_older )),
		label = "Your Birthday",
		required = True,
		initial = datetime.date(1980,1,1)
		)

	music_movies_books = forms.CharField(
		widget = forms.Textarea(),
		label = "Music, Movies and Books You Like",
		max_length = 2000,
		required = False,
		)

	friendship = forms.CharField(
		widget=forms.Textarea(),
		label = "What is your view on forming frienships via travel as an alternative to the typical tourist experince?",
		max_length = 2000,
		required = False,
		)

	what_will_you_show_visitors = forms.CharField(
		label = "What will you show visitors in your town?",
		required = True,
		max_length = 5000,
		widget=forms.Textarea(),
		)

	#Exclude City/User
	class Meta:
		model = UserProfile
		exclude = ('city','user')


class ExcursionRequestForm(forms.ModelForm):
	"""When the User requests the local to take him out, he fills this form"""

	#Traveler's message to the local
	message = forms.CharField(
		label='Message',

		widget=forms.Textarea(attrs={'placeholder': 'Introduce yourself and' 
			'share more about your plans with the local person.'})
		)

	#The date of the suggested outing or excursion 
	date = forms.DateField(label='Suggested Date for the Excursion')

	#Include the message and  the date
	class Meta:
		model = Request
		fields = ('message', 'date')


class LeaveReference_for_local(forms.ModelForm):
	"""User leaves reference for another user"""
	traveler_fun = forms.BooleanField(required=True, initial=True, label="Did you have fun with the local?")
	traveler_desc = forms.CharField(
		label='Reference Description',

		widget=forms.Textarea(attrs={'placeholder': 'Leave a reference here for the local that you met.'})
		)
	class Meta:
		model=RequestReference
		fields = ('traveler_fun', 'traveler_desc')

class LeaveReference_for_traveler(forms.ModelForm):
	"""User leaves reference for another user"""
	local_fun = forms.BooleanField(required=True, initial=True, label="Did you have fun with the traveler?")
	local_desc = forms.CharField(
		label='Reference Description',

		widget=forms.Textarea(attrs={'placeholder': 'Leave a reference here for the traveler that you met.'})
		)
	class Meta:
		model=RequestReference
		fields = ('local_fun', 'local_desc')


class CreateTripForm(forms.ModelForm):
	"""any user can post a public trip to a city, so that the locals there can see her/him"""

	#If the city is not in the database it'll be created (get_or_create)
	city_search_text = forms.CharField(
		label = "What city do you want to visit?",
		max_length = 200,
		required = True,

		#Any text input field with this id is connected to Google Autocomplete API
		widget=forms.TextInput(attrs={'id': 'google_city_search'})
		)

	#Traveler's message to the locals of that town (For ex: "Hey NY! I'm coming to you soon, would to love to meet up!")
	message = forms.CharField(label='Message',widget=forms.Textarea(attrs={'placeholder': 'Introduce yourself to the locals and share more about your plans.'}))
	
	#The date the traveler is available for an outing/excursion during her/his trip
	date = forms.DateField(label="Suggested Date when you're available for an excursion")

	#exclude city as it'll be processed seperately based on searched text
	#exclude traveler as it'll be passed from request
	class Meta:
		model = Excursion
		exclude = ('city', 'traveler')
		fields = ("city_search_text", 'date', 'message')


class OfferExcursionForm(forms.ModelForm):
	"""Local sees people coming to her/his town and offers one of them an outing/excursion around town"""

	#overriding init so that the local only sees trips for his city and for the traveler he's contacting
	def __init__(self, traveler=None, city=None, **kwargs):
		super(OfferExcursionForm, self).__init__(**kwargs)
		if traveler and city:
			self.fields['trip'].queryset = Excursion.objects.filter(city=city, traveler=traveler)
	
	#exclude local as it is passed via request (HTTP request)
	#exclude traveler approval as it'll be decided later
	#include message and trip
	class Meta:
		model = Offer
		exclude = ('local', 'traveler_approval')



class FeedbackForm(forms.Form):
	"""Feedback form"""

	#user Email address
	Your_Email_Address = forms.EmailField(required=True)

	#feedback message subject
	subject = forms.CharField(required=True)

	#feedback message
	message = forms.CharField(widget=forms.Textarea)


