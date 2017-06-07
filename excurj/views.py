from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from excurj.models import City, UserProfile, RequestReference, Request, User, Excursion, Offer
from django.db.models import Count
from django.contrib.auth.models import User
import population_script
from django.db.models import Q
from excurj.forms import UserForm, UserProfileForm, EditAccountForm, EditProfileForm, ExcursionRequestForm, CreateTripForm, OfferExcursionForm, FeedbackForm
from django.shortcuts import redirect
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import send_mail, BadHeaderError
from django.utils.safestring import mark_safe

#used for me to receive emails when a new user signs up or does other things
def send_me_email(subject, message, to_email):
	try:
		send_mail(subject,  message, '', to_email)
	except BadHeaderError:
		return HttpResponse('Invalid header found.')

def index(request):
	context_dict={}

	#brings back top 6 cities with the highest number of users
	city_list = City.objects.annotate(user_count=Count('city__user')).order_by('-user_count')[:6]
	
	refs= RequestReference.objects.select_related('request').filter(traveler_fun=True,local_fun=True).order_by('-request__date')[:2]
	
	context_dict['refs'] = refs

	context_dict['cities'] = city_list

	#bring back lat and lng for all cities to show them on Google Maps
	lat_lng_dict=[]
	all_cities = City.objects.select_related().annotate(count=Count('city__user'))
	for city in all_cities:
		lat_lng_entry = {
		'city_name' : city.name,
		'lat' : city.lat,
		'lng' : city.lng,
		'slug' : city.slug,
		'count' : city.count
		}

		if city.count == 1:
			print("KIIIIIIIIIIIIING: " + str(city.city.all()[0].prof_pic.url) + "CITY IS: " + str(city))
			lat_lng_entry['king_pic'] = str(city.city.all()[0].prof_pic.url)
		lat_lng_dict.append(lat_lng_entry)

	context_dict['all_cities'] =  mark_safe(lat_lng_dict)
	print(str(lat_lng_dict))
	
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
		excurjs = Excursion.objects.filter(traveler=user)

		context_dict['user'] = user
		context_dict['reqs'] = reqs
		context_dict['excurjs'] = excurjs

	except User.DoesNotExist:
		context_dict['user'] = None
		context_dict['reqs'] = None
		context_dict['excurjs'] = None

	return render(request, 'excurj/user.html', context_dict)

def search(request):

	if 'city-search' in request.GET:
		try:	
			send_me_email("NEW CITY SEARCH!!!!!! | excurj." , str(request.GET), ['moghrabi@gmail.com'])
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

	elif 'q' in request.GET:
		context_dict={}
		try:
			q = request.GET.get('q')
			send_me_email("NEW USER SEARCH!!!!!! | excurj." , str(request.GET), ['moghrabi@gmail.com'])
			

			users = User.objects.filter(Q(username__icontains=q)  
				| Q(first_name__icontains=q) | Q(last_name__icontains=q) 
				| Q(email__icontains=q) | Q(profile__city__name__icontains=q))

			context_dict['users'] = users

			return render(request, 'excurj/people_search.html', context_dict)

		except User.DoesNotExist:
			return HttpResponse("No profiles were returned based on this query :(")
		
def creat_city_object(city_search_text, profile):
	""" takes query string and UserProfile object and saves it in the user's profile - also work for createtrip view"""
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

	send_me_email("NEW USER!!!!!! | excurj." , request.user.username, ['moghrabi@gmail.com'])
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
			send_me_email("NEW EDIT PROFILE!!!!!! | excurj." , str(request.POST), ['moghrabi@gmail.com'])
			profile.save()
			
			return show_profile(request, request.user.username)

			# if 'next' in request.GET:
			# 	return redirect(request.GET['next'])
		else:
			print (profile_form.errors)
	else:
		if request.user.is_authenticated():
			edit_profile_form = EditProfileForm(instance=request.user.profile)
		else:
			return HttpResponseRedirect("/accounts/login/")



	return render(request, 'excurj/editprofile.html', {'edit_profile_form':edit_profile_form,})



def editaccount(request):
	if request.method == 'POST':
		edit_account_form = EditAccountForm(request.POST, instance=request.user)
		if edit_account_form.is_valid():
			edit_account_form.save()
			return show_profile(request, request.user.username)
			# if 'next' in request.GET:
			# 	return redirect(request.GET['next'])
	else:
		if request.user.is_authenticated():
			edit_account_form = EditAccountForm(instance=request.user)
		else:
			return HttpResponseRedirect("/accounts/login/")
		
		# edit_profile_form = EditProfileForm(instance=request.user.profile)

	return render(request, 'excurj/editaccount.html', {'edit_account_form':edit_account_form,})

def excursion_request(request, username):
	if request.method == 'POST':
		print("POOOOOOOOST" + str(request.POST))
		excursion_request_form = ExcursionRequestForm(request.POST)
		if excursion_request_form.is_valid():

			exj = excursion_request_form.save(commit=False)

			local_username = username
			print(local_username)

			local = User.objects.get(username=local_username)

			traveler = User.objects.get(username=request.user.username)
			message = request.POST['message']
			date = request.POST['date']

			exj.local = local
			exj.traveler=traveler
			exj.date=date
			exj.save()


			if 'next' in request.GET:
				return redirect(request.GET['next'])

		else:
			print(excursion_request_form.errors)

		excursion_request = Request.objects.create(local=local, traveler=traveler, message=message, date=date)

	else:
		if request.user.is_authenticated():
			excursion_request_form = ExcursionRequestForm()
		else:
			return HttpResponseRedirect("/accounts/login/")
	
	return render(request, 'excurj/excursionrequest.html', {'excursion_request_form':excursion_request_form})



def dashboard(request):
	context_dict={}
	if request.user.is_authenticated:
		#return the logged in user
		user = User.objects.get(username=request.user.username)
		context_dict['user'] = user

		#requests made by logged in user for others to take her out
		requests_i_made = Request.objects.filter(traveler=request.user)
		context_dict['requests_i_made'] = requests_i_made

		#others asked logged in user to take them out
		requests_others_made = Request.objects.filter(local=request.user)
		context_dict['requests_others_made'] = requests_others_made

		#upcoming trips for logged in user
		trips = Excursion.objects.filter(traveler=request.user)
		context_dict['trips'] = trips

		#excursions offers others have made
		offers = Offer.objects.filter(trip__traveler=request.user)
		context_dict['offers'] = offers

		#travelers coming to the logged in user's town soon
		upcoming_guests = Excursion.objects.filter(city=request.user.profile.city)
		context_dict['upcoming_guests'] = upcoming_guests

		did_user_make_offer = False 


		return render(request, 'excurj/dashboard.html', context_dict)

	else:
		return HttpResponseRedirect("/accounts/login/")

def createtrip(request):
	if request.method == 'POST':
		create_trip_form = CreateTripForm(request.POST)

		if create_trip_form.is_valid():
			trip = create_trip_form.save(commit=False)
			trip.traveler = request.user
			if 'city_search_text' in request.POST:
				creat_city_object(request.POST['city_search_text'], trip)

			is_trip_valid = True
			all_traveler_trips = Excursion.objects.filter(traveler=trip.traveler, city = trip.city)
			for t in all_traveler_trips:
				if trip.city == t.city:
					is_trip_valid = False
					break

			if is_trip_valid:
				trip.save()
			else:
				return HttpResponse("Sorry but you already made a trip to this city, if you think this message is a mistake please sned us a message through the feedback button in the corner")

			if 'next' in request.GET:
				return redirect(request.GET['next'])

		else:
			print(create_trip_form.errors)

	else:
		if request.user.is_authenticated():
			create_trip_form = CreateTripForm()
		else:
			return HttpResponseRedirect("/accounts/login/")
	return render(request, 'excurj/createtrip.html', {'create_trip_form':create_trip_form})

def offerexcursion(request, username):
	traveler = User.objects.get(username=username)
	if request.method == 'POST':
		offer_excursion_form = OfferExcursionForm(traveler=traveler, city=request.user.profile.city, data=request.POST)
		if offer_excursion_form.is_valid():
			offer = offer_excursion_form.save(commit=False)
			exj = Excursion.objects.get(traveler=traveler, city=request.user.profile.city)
			exj.local=request.user
			exj.save()
			offer.local = request.user
			offer.save()

			# try:
			# 	send_mail("Someone Offered to Take You Out! | excurj.", "test", "", [traveler.email,"moghrabi@gmail.com"])
			# except BadHeaderError:
			# 	return HttpResponse('Invalid header found.')

			send_me_email("Someone Offered to Take You Out! | excurj.", "test", [traveler.email,"moghrabi@gmail.com"])
			if 'next' in request.GET:
				return redirect(request.GET['next'])
		else:
			print(offer_excursion_form.errors)
	else:

		offer_excursion_form = OfferExcursionForm(traveler=traveler, city=request.user.profile.city)
	return render(request, 'excurj/offerexcursion.html', {'offer_excursion_form':offer_excursion_form})

def confirmoffer(request, offerid):
	offer = Offer.objects.get(id = offerid)
	if 'confirm' in request.GET:
		
		offer.traveler_approval = True
		subject = "Your offer has been confirmed! | excurj."
	else:
		offer.traveler_approval = False
		subject = "Your offer has been declined :( | excurj."
	offer.save()

	# try:
	# 	send_mail(subject, "test", "", [offer.local.email,"moghrabi@gmail.com"])
	# except BadHeaderError:
	# 	return HttpResponse('Invalid header found.')

	send_me_email(subject, "test", [offer.local.email,"moghrabi@gmail.com"])

	return HttpResponseRedirect("/dashboard/#excursionoffers")

def acceptrequest(request, requestid):
	requested = Request.objects.get(id = requestid)
	if 'accept' in request.GET:
		
		requested.local_approval = True
		subject = "Your request has been accepted! | excurj.".capitalize()
	else:
		requested.local_approval = False
		subject = "Your request has been declined :( | excurj.".capitalize()
	requested.save()

	# try:
	# 	send_mail(subject, "test", "", [offer.local.email,"moghrabi@gmail.com"])
	# except BadHeaderError:
	# 	return HttpResponse('Invalid header found.')

	send_me_email(subject, "test", [requested.traveler.email,"moghrabi@gmail.com"])

	return HttpResponseRedirect("/dashboard/#excursionoffers")

def feedback(request):
	
	if request.method == 'GET':
		feedback_form = FeedbackForm()
		
	else:
		feedback_form = FeedbackForm(data = request.POST)

		if feedback_form.is_valid():
			subject = feedback_form.cleaned_data['subject']
			Your_Email_Address = feedback_form.cleaned_data['Your_Email_Address']
			message = feedback_form.cleaned_data['message']
			message = message + "Wonderful client's email is: " + Your_Email_Address
			send_me_email("NEW FEEDBACK!!!!!! | excurj." , message, ['moghrabi@gmail.com'])
			return thankyou(request)

	return render(request, "excurj/feedback_email.html", {'feedback_form': feedback_form})

def thankyou(request):
    return render(request, "excurj/thankyousvg/index.html", {})


