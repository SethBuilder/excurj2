from django.shortcuts import render
from django.http import HttpResponse
from excurj.models import City, UserProfile, RequestReference, Request, User, Excursion
from django.db.models import Count
from django.contrib.auth.models import User
import population_script
from django.db.models import Q



def index(request):
	context_dict={}
	#brings back top 6 cities with the highest number of users
	city_list = City.objects.annotate(user_count=Count('userprofile')).order_by('-user_count')[:6]
	
	# reqs = Request.objects.filter(local_approval=True).order_by('-date')[:2]
	refs= RequestReference.objects.select_related('request').filter(traveler_fun=True,local_fun=True).order_by('-request__date')[:2]
	context_dict['refs'] = refs

	# for i in range(len(reqs)):
	# 	local_references_traveler = Reference.objects.filter(fun=True, author=reqs[i].local, referenced=reqs[i].traveler, local=True).latest()
	# 	traveler_references_local = Reference.objects.filter(fun=True, author=reqs[i].traveler, referenced=reqs[i].local, local=False).latest()
	# 	r = "req" + str(i)
	# 	context_dict[r] = {r : reqs[i], 
	# 	'local_references_traveler' : local_references_traveler, 'traveler_references_local' : traveler_references_local}
	# 	print(reqs)

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
		reqs = Request.objects.filter(local=user)
		context_dict['user'] = user

		context_dict['reqs'] = reqs

	except User.DoesNotExist:
		context_dict['user'] = None
		context_dict['reqs'] = None

	return render(request, 'excurj/user.html', context_dict)

def search(request):

	if 'city-search' in request.GET:
		try:
			searched_city = request.GET.get('city-search')
			print("SEARCHED CITY IS: " + searched_city.replace(" ", ""))

			
			searched_city_id = population_script.get_city_json(searched_city.replace(" ", ""))['results'][0]['id']
			
			if searched_city_id != -1:
				print("CITY ID: " + str(searched_city_id))
				city = City.objects.get(city_id = searched_city_id)
				return show_city(request, city.slug)

			else:
				return HttpResponse("There's no such city, please try a different query.")

		except City.DoesNotExist:
			context_dict={}
			cities = City.objects.filter(Q(name__icontains=searched_city) | Q(country__icontains=searched_city) | 
				Q(description__icontains=searched_city) | Q(slug__icontains=searched_city))
			context_dict['cities']=cities

			return render(request, 'excurj/cities_search.html', context_dict)

		# else:
		# 	return HttpResponse("This city isn't populated yet :( ")

	elif 'q' in request.GET:
		context_dict={}
		try:
			q = request.GET.get('q')
			

			users = User.objects.filter(Q(username__icontains=q)  
				| Q(first_name__icontains=q) | Q(last_name__icontains=q) 
				| Q(email__icontains=q) | Q(profile__city__name__icontains=q))

			context_dict['users'] = users

			return render(request, 'excurj/people_search.html', context_dict)

		except User.DoesNotExist:
			return HttpResponse("No profiles were returned based on this query :(")
		

	

	