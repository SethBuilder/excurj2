from django import forms
from django.contrib.auth.models import User
from excurj.models import UserProfile, City
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
