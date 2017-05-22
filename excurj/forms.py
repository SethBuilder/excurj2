from django import forms
from django.contrib.auth.models import User
from excurj.models import UserProfile, City,
from django.db import models


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_pic', 'city')


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