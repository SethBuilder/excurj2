from django.shortcuts import render
from django.http import HttpResponse
from excurj.models import City, UserProfile, Reference, Request, User, Excursion
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
		excursions = Excursion.objects.filter(city=city)

		context_dict['city']=city
		context_dict['city_locals_profiles']=city_locals_profiles
		context_dict['excursions'] = excursions

	except City.DoesNotExist:
		context_dict['city']=None

	except UserProfile.DoesNotExist:
		context_dict['city_locals_profiles']=None

	except Excursion.DoesNotExist:
		context_dict['excursions'] = None

	return render(request, 'excurj/city.html', context_dict)


def show_profile(request, username):
	context_dict={}

	try:
		user = User.objects.get(username=username)
		context_dict['user'] = user

		refs = Reference.objects.filter(referenced=user)# references others left about the user
		context_dict['refs'] = refs

	except User.DoesNotExist:
		context_dict['user'] = None
		context_dict['refs'] = None

	return render(request, 'excurj/user.html', context_dict)

