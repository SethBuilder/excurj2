from django.shortcuts import render
from django.http import HttpResponse
from excurj.models import City, UserProfile, Reference, Request, User
from django.db.models import Count
from django.contrib.auth.models import User


def index(request):
	context_dict={}
	#brings back top 6 cities with the highest number of users
	city_list = City.objects.annotate(user_count=Count('userprofile')).order_by('-user_count')[:6]
	
	reqs = Request.objects.filter(local_approval=True).order_by('-date')[:2]

	for i in range(len(reqs)):
		local_references_traveler = Reference.objects.filter(fun=True, author=reqs[i].local, referenced=reqs[i].traveler, local=True).latest()
		traveler_references_local = Reference.objects.filter(fun=True, author=reqs[i].traveler, referenced=reqs[i].local, local=False).latest()
		r = "req" + str(i)
		context_dict[r] = {r : reqs[i], 
		'local_references_traveler' : local_references_traveler, 'traveler_references_local' : traveler_references_local}
		print(reqs)

	context_dict['cities'] = city_list

	

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


	


