from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from excurj.models import City, UserProfile, RequestReference, Request, User, Excursion
from django.db.models import Count
from django.contrib.auth.models import User
import population_script
from django.db.models import Q
from excurj.forms import UserForm, UserProfileForm, EditAccountForm, EditProfileForm
from django.shortcuts import redirect
from django.core.exceptions import MultipleObjectsReturned


def index(request):
	context_dict={}
	#brings back top 6 cities with the highest number of users
	city_list = City.objects.annotate(user_count=Count('city__user')).order_by('-user_count')[:6]
	
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
		print()
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

	except City.MultipleObjectsReturned:
		city = City.objects.filter(slug=city_name_slug)[0]

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

		except IndexError:
			return HttpResponse("We couldn't find any city based on your query :( please pick from the list instead.")

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
		
def creat_city_object(city_search_text, profile):
	""" takes query string and UserProfile object and saves it in the user's profile"""
	try:

		searched_city_id = population_script.get_city_json(
		city_search_text.replace(" ", ""))['results'][0]['id']#brings back city ID from the Google API
		print("IDDDDDDDDDDDDDDDDD is: " + searched_city_id)

		# city = City.objects.get(city_id = searched_city_id)
		city = City.objects.get(city_id = searched_city_id)
		profile.city = city

	except City.DoesNotExist:
		city = population_script.populate_city(searched_city_id, city_search_text)
		# city = City.objects.create(city_id = searched_city_id)
		profile.city = city

	except IndexError:
		return HttpResponse("There's no such city, please pick a city from the list.")
	
def createprofile(request):
	if request.method =='POST':
		user = User.objects.get(username=request.user.username)
		
		user_form = UserForm(data=request.POST, instance=user)
		
		profile_form = UserProfileForm(data=request.POST)
		
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.save()

			profile = profile_form.save(commit=False)

			profile.user = user
			

			searched_city = request.POST['city_search_text']#brings back the city search result as text
			creat_city_object(searched_city, profile)
			# try:

			# 	searched_city_id = population_script.get_city_json(
			# 	searched_city.replace(" ", ""))['results'][0]['id']#brings back city ID from the Google API
			# 	print("IDDDDDDDDDDDDDDDDD is: " + searched_city_id)

			# 	# city = City.objects.get(city_id = searched_city_id)
			# 	city = City.objects.get(city_id = searched_city_id)
			# 	profile.city = city
			
			# except City.DoesNotExist:
			# 	city = population_script.populate_city(searched_city_id, searched_city)
			# 	# city = City.objects.create(city_id = searched_city_id)
			# 	profile.city = city

			# except IndexError:
			# 	return HttpResponse("There's no such city, please pick a city from the list.")


			if 'prof_pic' in request.FILES:#now save the profile pic
				profile.prof_pic = request.FILES['prof_pic']
				

			else:
				profile.prof_pic = 'profile_pictures/anon.png'

			profile.save()

			if 'next' in request.GET:
				return redirect(request.GET['next'])

		else:
			print (user_form.errors, profile_form.errors)

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()


	return render(request, 'excurj/createprofile.html', {'user_form':user_form, 'profile_form':profile_form})
	

def editprofile(request):
	if request.method == 'POST':
		edit_profile_form = EditProfileForm(request.POST, instance=request.user.profile)

		if edit_profile_form.is_valid():

			profile = edit_profile_form.save(commit=False)
			
			if 'prof_pic' in request.FILES:#now save the profile pic

				profile.prof_pic = request.FILES['prof_pic']

			else:
				profile.prof_pic = 'profile_pictures/anon.png'

			if 'city_search_text' in request.POST:
				creat_city_object(request.POST['city_search_text'], profile)

			profile.save()

			if 'next' in request.GET:
				return redirect(request.GET['next'])
		else:
			print (profile_form.errors)
	else:
		edit_profile_form = EditProfileForm(instance=request.user.profile)

	return render(request, 'excurj/editprofile.html', {'edit_profile_form':edit_profile_form,})



def editaccount(request):
	if request.method == 'POST':
		edit_account_form = EditAccountForm(request.POST, instance=request.user)
		if edit_account_form.is_valid():
			edit_account_form.save()

			if 'next' in request.GET:
				return redirect(request.GET['next'])
	else:
		edit_account_form = EditAccountForm(instance=request.user)
		# edit_profile_form = EditProfileForm(instance=request.user.profile)

	return render(request, 'excurj/editaccount.html', {'edit_account_form':edit_account_form,})
