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
        


# class UpdateUserForm(forms.ModelForm):
#     username = forms.CharField(required=True)
#     email = forms.EmailField(required=True)
#     first_name = forms.CharField(required=False)
#     last_name = forms.CharField(required=False)

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name', 'last_name')

#     def save(self, commit=True):
#         user = super(UpdateUserForm, self).save(commit=False)

#         if commit:
#             user.save()

#         return user


# class UpdateProfileForm(forms.ModelForm):
#     city = models.ForeignKey(City)

#     class Meta:
#         model = UserProfile
#         fields = ('city', 'profilepic', 'hobbies', 'languages')

#     def save(self, commit=True):
#         profile = super(UpdateProfileForm, self).save(commit=False)

#         if commit:
#             profile.save()
#         return profile