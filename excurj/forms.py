from django import forms
from django.contrib.auth.models import User
from excurj.models import UserProfile, City, Request, Excursion, Offer
from django.db import models


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


class UserProfileForm(forms.ModelForm):
	city_search_text = forms.CharField(
		label = "Your Current City:",
		max_length = 200,
		required = True,
		)
	class Meta:
	    model = UserProfile
	    exclude = ('city','user')
	    # fields = ('city_search_text','city','prof_pic', 'dob', 'sex', 'education', 'career', 'about_you', 
	    # 	'music_movies_books','friendship','what_will_you_show_visitors', )
        

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('city','user')#I'm testing to update these fields


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


