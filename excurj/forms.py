from django import forms
from django.contrib.auth.models import User
from excurj.models import UserProfile, City, Request, Excursion, Offer
from django.db import models
import datetime

#The part of the User form displayed along with profile form
class UserForm(forms.ModelForm):
	first_name = forms.CharField(
		label = "First Name:",
		max_length = 80,
		required = True
		)

	last_name = forms.CharField(
		label = "Last Name:",
		max_length = 80,
		required = True,
		)

	class Meta:
	    model = User
	    fields = ('first_name', 'last_name')

#Form for editing the account
class EditAccountForm(forms.ModelForm):
	class Meta:
		model = User
		exclude = ('password','is_staff', 'is_active', 'user_permissions', 'groups', 
			'date_joined', 'last_login', 'date_joined', 'is_superuser')

	def save(self, commit=True):
		user = super(EditAccountForm, self).save(commit=False)

		if commit:
		    user.save()
		return user

#used to ensure users are 13 years and older
def get_current_year():
	
	now = datetime.datetime.now() 
	return now.year

_13_or_older = get_current_year() -13


#Profile form
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
		label = "What is your view on forming frienships via travel as an alternative to the typical tourist experince?",
		required=False,
		max_length=2000,
		)
	what_will_you_show_visitors = forms.CharField(
		label = "What will you show visitors in your town?",
		required = True,
		widget=forms.Textarea(),
		max_length=5000
		)
	class Meta:
	    model = UserProfile
	    exclude = ('city','user')
	    # fields = ('city_search_text','city','prof_pic', 'dob', 'sex', 'education', 'career', 'about_you', 
	    # 	'music_movies_books','friendship','what_will_you_show_visitors', )



#Edit profile form
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
	class Meta:
		model = UserProfile
		exclude = ('city','user')


class ExcursionRequestForm(forms.ModelForm):
	message = forms.CharField(
		label='Message',
		widget=forms.Textarea(attrs={'placeholder': 'Introduce yourself and share more about your plans with the local person.'}))
	date = forms.DateField(label='Suggested Date for the Excursion')
	class Meta:
		model = Request
		fields = ('message', 'date')


class CreateTripForm(forms.ModelForm):
	city_search_text = forms.CharField(
		label = "What city do you want to visit?",
		max_length = 200,
		required = True,
		widget=forms.TextInput(attrs={'id': 'google_city_search'})
		)
	message = forms.CharField(label='Message',widget=forms.Textarea(attrs={'placeholder': 'Introduce yourself to the locals and share more about your plans.'}))
	date = forms.DateField(label="Suggested Date when you're available for an excursion")
	class Meta:
		model = Excursion
		exclude = ('city', 'traveler')
		fields = ("city_search_text", 'date', 'message')


class OfferExcursionForm(forms.ModelForm):
	def __init__(self, traveler=None, city=None, **kwargs):
		super(OfferExcursionForm, self).__init__(**kwargs)
		if traveler and city:
			self.fields['trip'].queryset = Excursion.objects.filter(city=city, traveler=traveler)
	class Meta:
		model = Offer
		exclude = ('local', 'traveler_approval')

class FeedbackForm(forms.Form):
    Your_Email_Address = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea)


