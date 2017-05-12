from django.shortcuts import render
from django.http import HttpResponse
from excurj.models import City, UserProfile
from django.db.models import Count
from django.contrib.auth.models import User


def index(request):
	#brings back top 5 cities with the highest number of users
	city_list = City.objects.annotate(user_count=Count('userprofile')).order_by('-user_count')[:5]
	context_dict = {'cities' : city_list}

	return render(request, 'excurj/index.html', context_dict)

def show_city(request, city_name_slug):
	context_dict={}

	try:
		city = City.objects.get(slug=city_name_slug)
		city_locals_profiles = UserProfile.objects.filter(city=city)

		context_dict['city']=city
		context_dict['city_locals_profiles']=city_locals_profiles

	except City.DoesNotExist:

		context_dict['city']=None
		context_dict['city_locals_profiles']=None

	return render(request, 'excurj/city.html', context_dict)


	


