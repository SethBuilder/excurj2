from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from excurj.models import City, UserProfile, RequestReference, Request, User, Excursion, Offer
from django.db.models import Count
from django.contrib.auth.models import User
import population_script
from django.db.models import Q
from excurj.forms import UserForm, UserProfileForm, EditAccountForm, EditProfileForm, \
 ExcursionRequestForm, CreateTripForm, OfferExcursionForm, FeedbackForm, LeaveReference_for_traveler, \
 LeaveReference_for_local
from datetime import datetime
from django.shortcuts import redirect
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import send_mail, BadHeaderError
from django.utils.safestring import mark_safe
import urllib.request, json
import requests
import dateutil.parser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from time import sleep
from django.utils.timezone import localtime
from django.contrib.auth import login, authenticate
from django.http import JsonResponse



def send_me_email(subject, message, to_email):
	"""Used so I receive emails when a new user signs up or does other things like send feedback"""
	try:
		send_mail(subject,  message, '', to_email)
	except BadHeaderError:
		return HttpResponse('Invalid header found.')


def index(request):
	context_dict={}

	# print("taaaaaaaaaaaaaaask is: " + str(fact.delay(20000).get(propagate=False)))

	#brings back top 6 cities with the highest number of users
	city_list = City.objects.annotate(user_count=Count('city__user')).order_by('-user_count')[:6]
	
	#The two references that are based on the front page
	#Currently featured references are from Requests (traveler asks local to take her out) 
		#and not offers (when local offers traveler to take him out)
	refs= RequestReference.objects.select_related('request') \
	.filter(traveler_fun=True,local_fun=True) \
	.order_by('-request__date')[:2]

	# refs = reversed(refs)
	
	context_dict['refs'] = refs

	context_dict['cities'] = city_list

	#bring back lat and lng for all cities to show them on the Google Maps
	lat_lng_dict=[]

	#Pull all cities to feature them on the Google Map with the number of users for each one
	all_cities = City.objects.select_related().annotate(count=Count('city__user'))

	#Loop thru cities and pull their name, lat, lng, slug and number of users
	for city in all_cities:
		if city.lat != None and city.name != '':
			lat_lng_entry = {
			'city_name' : city.name,
			'lat' : city.lat,
			'lng' : city.lng,
			'slug' : city.slug,
			'count' : city.count
			}

		#If the user only has one user then include her/his profile picture to feature it on the map marker pop up
		if city.count == 1:

			#A lonely user is called King as I might give royal titles to the first users of each city
			lat_lng_entry['king_pic'] = str(city.city.all()[0].prof_pic.url)

			#append city's lat and lng to the lat lng dictionary
			lat_lng_dict.append(lat_lng_entry)

		

	context_dict['all_cities'] =  mark_safe(lat_lng_dict)
	
	return render(request, 'excurj/index.html', context_dict)

def index_amp(request):
	context_dict={}

	# print("taaaaaaaaaaaaaaask is: " + str(fact.delay(20000).get(propagate=False)))

	#brings back top 6 cities with the highest number of users
	city_list = City.objects.annotate(user_count=Count('city__user')).order_by('-user_count')[:6]
	
	#The two references that are based on the front page
	#Currently featured references are from Requests (traveler asks local to take her out) 
		#and not offers (when local offers traveler to take him out)
	refs= RequestReference.objects.select_related('request') \
	.filter(traveler_fun=True,local_fun=True) \
	.order_by('-request__date')[:2]

	# refs = reversed(refs)
	
	context_dict['refs'] = refs

	context_dict['cities'] = city_list

	#bring back lat and lng for all cities to show them on the Google Maps
	# lat_lng_dict=[]

	# #Pull all cities to feature them on the Google Map with the number of users for each one
	# all_cities = City.objects.select_related().annotate(count=Count('city__user'))

	# #Loop thru cities and pull their name, lat, lng, slug and number of users
	# for city in all_cities:
	# 	lat_lng_entry = {
	# 	'city_name' : city.name,
	# 	'lat' : city.lat,
	# 	'lng' : city.lng,
	# 	'slug' : city.slug,
	# 	'count' : city.count
	# 	}

	# 	#If the user only has one user then include her/his profile picture to feature it on the map marker pop up
	# 	if city.count == 1:

	# 		#A lonely user is called King as I might give royal titles to the first users of each city
	# 		lat_lng_entry['king_pic'] = str(city.city.all()[0].prof_pic.url)

	# 	#append city's lat and lng to the lat lng dictionary
	# 	lat_lng_dict.append(lat_lng_entry)

		

	# context_dict['all_cities'] =  mark_safe(lat_lng_dict)
	
	return render(request, 'excurj/index_amp.html', context_dict)


def cities_list(request):
	context_dict={}

	#brings back top all cities with the highest number of users
	city_list = City.objects.annotate(user_count=Count('city__user')).order_by('-user_count')

	page = request.GET.get('page', 1)

	searched_query = request.GET.get('city-search', 'nothing')

	print("PAIGE IS "  + str(request))
	paginator = Paginator(city_list, 6)

	try:
		# sleep(2)
		cities = paginator.page(page)
	except PageNotAnInteger:
		cities = paginator.page(1)
	except EmptyPage:
		cities = paginator.page(paginator.num_pages)
	except:
		pass

	context_dict['cities'] = cities
	context_dict['searched_query'] = searched_query
	print(str(context_dict))
	
	
	return render(request, 'excurj/cities.html', context_dict)


def get_perma_fb_token():
	token = get_json_raw("https://graph.facebook.com/oauth/access_token?client_id=262023620939242&client_secret=13a20efc5cb8245237e8a8d08118abe1&grant_type=client_credentials")

def get_json_raw(url):
	"""takes facebook graph url and returns raw json"""
	response = requests.get(url)
	jsondata = json.loads(response.text)
	
	return jsondata

def pull_events(city):
	events=[]
	# url = 'https://graph.facebook.com/search?q=%s&type=event&access_token=EAADuTyDZATeoBAEO0VFZCZCROVUmhAdqE8ZCXFpQLqh4F3KRZCL9EIJ3N9MJZA4AUcVrNCJg077Oh80XJiyWwbLLmJiN7dFnSxm1OCm04ZCbuICDNvwlLMDhbUv3iYOzdEBPBKcZBSLUuQlyhZCPxeqsfhDscYQuIMGhZBq2EZCt0D4jQZDZD&token_type=bearer' % city.name.replace(' ', '')
	url = 'https://www.eventbriteapi.com/v3/events/search?token=6HXJMYZIFBDCKGFA5C6E&q=%s&sort_by=date' % city.name.replace(' ', '')
	events_json = get_json_raw(url)

	# print(events_json)

	# try:
	# # If no events were returned, try using the first level of the city name as query (Amman instead of Amman, Jordam)
	# 	if len(events_json['events']) == 0:
	# 		try_differeny_city_name = city.name.split(',');
	# 		try_differeny_city_name = try_differeny_city_name[0] + ',' + try_differeny_city_name[len(try_differeny_city_name) -1]

			
	# 		#PULL LOCAL EVENTS
	# 		url = 'https://graph.facebook.com/search?q=%s&type=event&access_token=EAADuTyDZATeoBAEO0VFZCZCROVUmhAdqE8ZCXFpQLqh4F3KRZCL9EIJ3N9MJZA4AUcVrNCJg077Oh80XJiyWwbLLmJiN7dFnSxm1OCm04ZCbuICDNvwlLMDhbUv3iYOzdEBPBKcZBSLUuQlyhZCPxeqsfhDscYQuIMGhZBq2EZCt0D4jQZDZD&token_type=bearer' % try_differeny_city_name.replace(' ', '')
			
	# 		events_json = get_json_raw(url)
	# 		print("WHYYYY" + events_json)

	# except Exception:
	# 	pass


		
		

	#Loop thru events and send list of events
	for event in events_json['events'][:6]:

		# pull event cover photo
		venue_url = 'https://www.eventbriteapi.com/v3/venues/{0}?token=6HXJMYZIFBDCKGFA5C6E'.format(event['venue_id'])
		
		event_photo_json = get_json_raw(venue_url)
		if 'name' in event_photo_json:
			event['venue_name'] = event_photo_json['name']
		if 'address' in event_photo_json:
			event['venue_address'] = event_photo_json['address']['localized_address_display']

		if 'latitude' in event_photo_json:
			event['lat'] = event_photo_json['latitude']

		if 'longitude' in event_photo_json:
			event['lng'] = event_photo_json['longitude']

		# Pull venue image
		# venue_photo_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query={0}&location={1},{2}&radius=10000&key=AIzaSyAC9SSvIEbSOt7ocozi4AxBoFqOz7ZX2Wc'.format(event['venue_address'], event_photo_json['longitude'], event_photo_json['latitude'])
		# event_photo_json = get_json_raw(venue_photo_url)
		# print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'+str(event_photo_json['results']))
		# if 'type' in event_photo_json:
		# 	event['type'] = event_photo_json['type']
		
		#append event to events list
		events.append(event)
	
	return events


def pull_city(city_name_slug):
	try:

		#Try pull the City object from the passed slug
		city = City.objects.get(slug=city_name_slug)

	#Error message will be shown if the city being searched does not exist
	except City.DoesNotExist:
		context_dict['city']=None


	#If more than one city returned (for whatever reason) then return the first one
	except City.MultipleObjectsReturned:
		city = City.objects.filter(slug=city_name_slug)[0]

	return city

def show_city(request, city_name_slug):
	""" Django View to show city profile page """

	context_dict={}

	try:

		#Try pull the City object from the passed slug
		city = pull_city(city_name_slug)
		
		#Pull associated user profiles to feature them under the "Locals" tab
		city_locals_profiles = UserProfile.objects.filter(city=city)

		#Pull trips to this city to feature them under "People coming to this city soon"
		excursions = Excursion.objects.filter(city=city)

		context_dict['city']=city
		context_dict['city_locals_profiles']=city_locals_profiles
		context_dict['excursions'] = excursions

	except UserProfile.DoesNotExist:
		context_dict['city_locals_profiles']=None

	except Excursion.DoesNotExist:
		context_dict['excursions'] = None
	except Exception:
		pass

	# Pull city events from the Facebook Graph
	events = pull_events(city)

	context_dict['events'] = events

	return render(request, 'excurj/city.html', context_dict)

def eventdetails(request, cityslug, eventid):

	city = pull_city(cityslug)
	events = pull_events(city)
	
	context_dict={}

	event_in_question = [event for event in events if event['id'] == eventid]



	context_dict['event'] = event_in_question
	# print("EVENTTT IS: " + str(event_in_question))
	
	context_dict['venue_image'] = pull_venue_image(event_in_question,cityslug)

	event_date = event_in_question[0]['start']['local']
	# print('ddddddddddddddddddd'+event_date)

	# date = dateutil.parser.parse(event_date)
	# offset = dateutil.parser.parse(event_date).tzinfo._offset

	# readable_event_date = (date + offset).strftime('%a, %b %d %Y %I:%M:%S %p')

	# print("START TIME IS: " + str(event_date))

	context_dict['event_time'] = event_date

	context_dict['city'] = city


	return render(request, 'excurj/event.html', context_dict)

def pull_venue_image(event_in_question, cityslug):
	
	try:
		
		if 'place' in event_in_question[0]:
			venue_name = event_in_question[0]['place']['name']
			venue_lat = event_in_question[0]['place']['location']['latitude']
			venue_long = event_in_question[0]['place']['location']['longitude']
		else:
			venue_name="Venue details not available."
			
			venue_lat = 0
			venue_long = 0
		url = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=500&type=venue&keyword=%s&key=%s') % (venue_lat, venue_long, venue_name, population_script.get_google_key())

		#retrieve the profile pic
	
		response = requests.get(url)
		jsondata = json.loads(response.text)
		
		venue_photo_reference = jsondata['results'][0]['photos'][0]['photo_reference']

		venue_image = ('https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference=%s&key=%s') % (venue_photo_reference, population_script.get_google_key())
		
		return venue_image

	except requests.exceptions.ConnectionError as e:
		e.status_code = 'Connection refused'
		print(e.status_code)
		venue_image = -1
		return venue_image

	except IndexError:
		venue_image = -1

		return venue_image

	#use geocode to pull lat and long
	except KeyError:
		geo_code_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=AIzaSyAC9SSvIEbSOt7ocozi4AxBoFqOz7ZX2Wc' % venue_name
		geo_code_response = get_json_raw(geo_code_url)

		#now pull lat and long
		print("GEOOOO" + str(geo_code_response['results'][0]['geometry']['location']))
		venue_lat = geo_code_response['results'][0]['geometry']['location']['lat']
		venue_long = geo_code_response['results'][0]['geometry']['location']['lng']
		
		url = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=500&type=venue&keyword=%s&key=%s') % (venue_lat, venue_long, venue_name, population_script.get_google_key())

		#retrieve the profile pic
	
		response = requests.get(url)
		jsondata = json.loads(response.text)

		print("PHOTOOOOOOO" + str(jsondata))
		
		try:
			venue_photo_reference = jsondata['results'][0]['photos'][0]['photo_reference']
			venue_image = ('https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference=%s&key=%s') % (venue_photo_reference, population_script.get_google_key())
			return venue_image
		except:
			venue_image = -1
			return venue_image


def show_profile(request, username):
	"""View for User Profile"""
	context_dict={}


	try:
		#Pull the user based on the passed username
		user = User.objects.get(username=username)

		#all the excursion requests made to the user as a local
		reqs_as_local = Request.objects.filter(local=user)
		#all requests made to the user whose profile is being browsed (as a traveler)
		reqs_as_traveler = Request.objects.filter(traveler=user)

 		#The logged in user is the traveler in this case
		show_review_button_for_traveler = False

		#show review button on the local profile
		for req in reqs_as_traveler:
			print("REQ IS: " + str(req))
			
			if req.traveler == user and req.local == request.user:
				try:
					ref = RequestReference.objects.get(pk = req.id)
					print("REFFFFF 1: " + str(ref))
				except RequestReference.DoesNotExist:
					ref = RequestReference.objects.create(pk = req.id)
					print("REFFFFF 2: " + str(ref))
				if ref.local_desc in [None, '']:
					show_review_button_for_traveler = True
					print("show_review_button_for_traveler 1: " + str(show_review_button_for_traveler))
					
				else:
					show_review_button_for_traveler = False
					print("show_review_button_for_traveler 2: " + str(show_review_button_for_traveler))
					
			else:
				show_review_button_for_traveler = False
				print("show_review_button_for_traveler 3: " + str(show_review_button_for_traveler))





		#The logged in user is the local in this case
		show_review_button_for_local = False

		#show review buton on the traveler profile
		for req in reqs_as_local:
			
			if req.local == user and req.traveler == request.user:
				try:
					ref = RequestReference.objects.get(pk = req.id)
					print("REFFFFF : " + str(ref))
				except RequestReference.DoesNotExist:
					ref = RequestReference.objects.create(pk = req.id)
					print("REFFFFF : " + str(ref))
				if ref.traveler_desc in [None, '']:
					show_review_button_for_local = True
					print("show_review_button_for_local 1: " + str(show_review_button_for_local))
					
				else:
					show_review_button_for_local = False
					print("show_review_button_for_local 2: " + str(show_review_button_for_local))
					
			else:
				show_review_button_for_local = False
				print("show_review_button_for_local 3: " + str(show_review_button_for_local))









		#Pull users upcoming trips
		excurjs = Excursion.objects.filter(traveler=user)

		context_dict['user'] = user
		context_dict['reqs_as_local'] = reqs_as_local
		context_dict['excurjs'] = excurjs
		context_dict['show_review_button_for_traveler'] = show_review_button_for_traveler
		context_dict['show_review_button_for_local'] = show_review_button_for_local

	except User.DoesNotExist:
		context_dict['user'] = None
		context_dict['reqs_as_local'] = None
		context_dict['excurjs'] = None


	return render(request, 'excurj/user.html', context_dict)

def search(request):
	"""
		View for the search features - 
		the one on the homepage to search cities and the one in the nav bar to search people (users)
	"""

	#if user searches for a city
	if 'city-search' in request.GET:
		try:	
			#Send me Email
			# send_me_email("NEW CITY SEARCH!!!!!! | excurj." , str(request.GET), ['moghrabi@gmail.com'])

			#Pull the search text
			searched_city = request.GET.get('city-search')
			
			print("IDDDDD is" + str(population_script.get_city_json(searched_city.replace(" ", ""))))
			#Pass on the searched text for a city and pull the ID (from Google Places API)
			searched_city_id = population_script.get_city_json(searched_city.replace(" ", ""))['results'][0]['id']
			
			#If city ID is returned
			if searched_city_id != -1:
				print("IDDDDD is" + searched_city_id)
				
				#Pull city from the database and return the appropriate city profile
				city = City.objects.get(city_id = searched_city_id)

				if city.slug != "":
					return show_city(request, city.slug)

			#If no city ID was returned from the Google API (very rarely the case)
			else:
				# return HttpResponse("There's no such city, please try a different query.")
				print("No such city!")
				return cities_list(request)

		#If the user searched for a city that does not exist in the database 
		except City.DoesNotExist:

			context_dict={}

			#Then, pull other populated cities that match the query
			cities = City.objects.filter(

				  #Based on city name
				  Q(name__icontains=searched_city) \

				  #Or country name
				| Q(country__icontains=searched_city) \

				  #Or city description
				| Q(description__icontains=searched_city) \

				  #Or city's slug
				| Q(slug__icontains=searched_city) \

				) 
			if cities.exists():
				context_dict['cities']=cities
				return render(request, 'excurj/cities_search.html', context_dict)
			else:
				return cities_list(request)


		#If no query matches found
		# except IndexError:
		except Exception:
			print("INDEX ERROR")
			#If num of cities is 0 return all cities (never ending scroll of cities)
			return cities_list(request)

	#Is user is searching for a person (in the nav bar)
	elif 'q' in request.GET:

		context_dict={}

		try:
			#Pull search query
			q = request.GET.get('q')

			#Send me email
			send_me_email("NEW USER SEARCH!!!!!! | excurj." , str(request.GET), ['moghrabi@gmail.com'])
			

			#Match query with existing users, based on:
			users = User.objects.filter(

				  #Based on username
				  Q(username__icontains=q)  \

				  #Or first name
				| Q(first_name__icontains=q) \

				  #Or last name
				| Q(last_name__icontains=q) \

				  #OR email address
				| Q(email__icontains=q) \

				  #Or city name
				| Q(profile__city__name__icontains=q) \

				)

			context_dict['users'] = users

			return render(request, 'excurj/people_search.html', context_dict)

		#If no users were found based on the search query
		except User.DoesNotExist:
			return HttpResponse("No profiles were returned based on this query :(")




def creat_city_object(city_search_text, profile):
	""" 
		Takes query string for a city from the Google autocomplete API, 
		then it whether pulls the city or creates it.

		Used for User signups, updating profiles
	"""

	try:

		#Pull City ID from the Google API
		searched_city_id = population_script.get_city_json( city_search_text.replace(" ", ""))['results'][0]['id']

		#If city is in the database pull it and save it to the profile
		city = City.objects.get(city_id = searched_city_id)
		profile.city = city

	#If city doesn't not exist in the database but has valid Google API ID
	except City.DoesNotExist:

		#Create it and save it to the profile
		city = population_script.populate_city(searched_city_id, city_search_text)
		profile.city = city

	#If no City ID was returned (like when the user searches for: fdhjhdjfhdjskfhjh)
	except IndexError:
		return HttpResponse("There's no such city, please pick a city from the list.")
	
def createprofile(request):
	"""View to create profile"""

	#If request is POST, pull data and save it
	if request.method =='POST':

		# user = User.objects.get(username=request.user.username)
		user_form = UserForm(data=request.POST)# took this out:instance=user
		profile_form = UserProfileForm(data=request.POST)
		
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			login(request, user)
			user.save()

			username = user_form.cleaned_data.get('username')
			raw_password = user_form.cleaned_data.get('password')
			# user = authenticate(username=username, password=raw_password)
			login(request, user)

			#commit = false so that we can save profile pic and process city search query
			profile = profile_form.save(commit=False)

			profile.user = user
			
			#brings back the city search query
			searched_city = request.POST['city_search_text']

			#Get or create the city
			creat_city_object(searched_city, profile)
			# try:

			#now save the profile pic
			if 'prof_pic' in request.FILES:
				profile.prof_pic = request.FILES['prof_pic']
				
			else:
				profile.prof_pic = 'profile_pictures/anon.png'

			profile.save()
			send_me_email("NEW USER!!!!!! | excurj." , request.user.username, ['moghrabi@gmail.com'])
			return JsonResponse({'success':"success"})

			#direct user to index page
			if 'next' in request.GET:
				# send_me_email("NEW USER!!!!!! | excurj." , request.user.username, ['moghrabi@gmail.com'])
				# return redirect(request.GET['next'])
				return JsonResponse({'success':"success"})

		else:
			print (user_form.errors, profile_form.errors)

	#If request is GET then show forms
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'excurj/createprofile.html', {'user_form':user_form, 'profile_form':profile_form})
	

def editprofile(request):
	""" View to edit profile """

	if request.method == 'POST':
		#pull user's profile data by passing an instance of the profile
		edit_profile_form = EditProfileForm(request.POST, instance=request.user.profile)

		if edit_profile_form.is_valid():

			profile = edit_profile_form.save(commit=False)
			if 'prof_pic' in request.FILES:#now save the profile pic

				profile.prof_pic = request.FILES['prof_pic']
			elif profile.prof_pic != " /media/profile_pictures/anon.png ":
				pass
			else:
				profile.prof_pic = 'profile_pictures/anon.png'

			#If user changed his city, then process search query and save resulting city it in his profile
			if 'city_search_text' in request.POST:
				creat_city_object(request.POST['city_search_text'], profile)

			#send me email
			send_me_email("NEW EDIT PROFILE!!!!!! | excurj." , str(request.POST), ['moghrabi@gmail.com'])

			#Save updated profile
			profile.save()
			
			#Return user to his profile page
			return show_profile(request, request.user.username)

		else:
			print (profile_form.errors)
	
	#If user attempts to go to /editprofile/ but he's not authenticated then forward rqeuest to /accounts/login/
	else:
		if request.user.is_authenticated():
			edit_profile_form = EditProfileForm(instance=request.user.profile)
		else:
			return HttpResponseRedirect("/login/")

	return render(request, 'excurj/editprofile.html', {'edit_profile_form':edit_profile_form,})



def editaccount(request):
	"""Edit account view"""

	#Pass User instance to pull already filled data
	if request.method == 'POST':
		edit_account_form = EditAccountForm(request.POST, instance=request.user)
		if edit_account_form.is_valid():
			edit_account_form.save()
			return show_profile(request, request.user.username)

	#If user is not authenticated and goes to /editaccount/ then forward her to /accounts/login/
	else:
		if request.user.is_authenticated():
			edit_account_form = EditAccountForm(instance=request.user)
		else:
			return HttpResponseRedirect("/login/")

	return render(request, 'excurj/editaccount.html', {'edit_account_form':edit_account_form,})

def excursion_request(request, username):
	"""View for when traveler requests local to take him/her out"""
	if request.method == 'POST':
		
		excursion_request_form = ExcursionRequestForm(request.POST)
		if excursion_request_form.is_valid():
			exj = excursion_request_form.save(commit=False)
			local_username = username
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
			return HttpResponseRedirect("/login/")
	
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

		return render(request, 'excurj/dashboard.html', context_dict)

	else:
		return HttpResponseRedirect("/login/")


def createtrip(request):
	"""View for when users create public trips on their dashboard"""

	if request.method == 'POST':
		create_trip_form = CreateTripForm(request.POST)

		if create_trip_form.is_valid():
			trip = create_trip_form.save(commit=False)
			trip.traveler = request.user
			if 'city_search_text' in request.POST:
				creat_city_object(request.POST['city_search_text'], trip)

			#Currently, users are able to only make one trip to the same city
			#TO_DO: after the date has passed for the trip, send review request and archive trip into offline table
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
			return HttpResponseRedirect("/login/")

	return render(request, 'excurj/createtrip.html', {'create_trip_form':create_trip_form})

def offerexcursion(request, username):
	""" View for when local offers excursions to visitors """

	traveler = User.objects.get(username=username)
	if request.method == 'POST':
		offer_excursion_form = OfferExcursionForm(traveler=traveler, city=request.user.profile.city,\
		 data=request.POST)
		if offer_excursion_form.is_valid():
			offer = offer_excursion_form.save(commit=False)
			exj = Excursion.objects.get(traveler=traveler, city=request.user.profile.city)
			exj.local=request.user
			exj.save()
			offer.local = request.user
			offer.save()

			#Send email to traveler (and moi)
			send_me_email("Someone Offered to Take You Out! | excurj.", "test", [traveler.email,"moghrabi@gmail.com"])

			if 'next' in request.GET:
				return redirect(request.GET['next'])
		else:
			print(offer_excursion_form.errors)
	else:

		offer_excursion_form = OfferExcursionForm(traveler=traveler, city=request.user.profile.city)
	return render(request, 'excurj/offerexcursion.html', {'offer_excursion_form':offer_excursion_form})



def leavereview_for_traveler(request, username):
	""" logged in user is the local - profile being reviewed is the traveler """

	excursion_request = Request.objects.filter(traveler__username = username, local = request.user).latest()
	reference = RequestReference.objects.filter(request = excursion_request).latest()
	referenced_person_name = User.objects.get(username=username).first_name.title()
	

	if request.method == 'POST':
		leavereview_for_traveler_form = LeaveReference_for_traveler(data=request.POST)
		if leavereview_for_traveler_form.is_valid():
			ref = leavereview_for_traveler_form.save(commit=False)
			ref.request = excursion_request
			ref.traveler_desc = reference.traveler_desc
			ref.save()

			if 'next' in request.GET:
				return redirect(request.GET['next'])

		else:
			print(leavereview_for_traveler_form.errors)
	else:
		leavereview_for_traveler_form = LeaveReference_for_traveler()
	return render(request, 'excurj/leavereview_for_traveler.html',\
	 {'leavereview_for_traveler_form':leavereview_for_traveler_form,\
	 'referenced_person_name': referenced_person_name})

	#Send email
	# 

	return HttpResponseRedirect("/")


def leavereview_for_local(request, username):
	""" logged in user is the traveler - profile being reviewed is the local """

	excursion_request = Request.objects.filter(local__username = username, traveler=request.user).latest()
	reference = RequestReference.objects.filter(request = excursion_request).latest()
	referenced_person_name = User.objects.get(username=username).first_name.title()

	if request.method == 'POST':
		leavereview_for_local_form = LeaveReference_for_local(data=request.POST)
		if leavereview_for_local_form.is_valid():
			ref = leavereview_for_local_form.save(commit=False)
			ref.request = excursion_request
			ref.local_desc = reference.local_desc
			ref.save()

			if 'next' in request.GET:
				return redirect(request.GET['next'])

		else:
			print(leavereview_for_local_form.errors)
	else:
		leavereview_for_local_form = LeaveReference_for_local()

	return render(request, 'excurj/leavereview_for_local.html',\
	 {'leavereview_for_local_form':leavereview_for_local_form, \
	 'referenced_person_name': referenced_person_name})

	#Send email
	

	return HttpResponseRedirect("/")











def confirmoffer(request, offerid):
	""" Confirm offer view """

	offer = Offer.objects.get(id = offerid)
	if 'confirm' in request.GET:
		
		offer.traveler_approval = True
		subject = "Your offer has been confirmed! | excurj."
	else:
		offer.traveler_approval = False
		subject = "Your offer has been declined :( | excurj."
	offer.save()

	#Send email
	send_me_email(subject, "test", [offer.local.email,"moghrabi@gmail.com"])

	return HttpResponseRedirect("/dashboard/#excursionoffers")

def acceptrequest(request, requestid):
	""" view to accept traveler's request for an excursion """

	#Requested is the request
	traveler_request = Request.objects.get(id = requestid)
	
	if 'accept' in request.GET:
		
		traveler_request.local_approval = True
		subject = "Your request has been accepted! | excurj.".capitalize()
	else:
		traveler_request.local_approval = False
		subject = "Your request has been declined :( | excurj.".capitalize()

	traveler_request.save()

	#Send email
	send_me_email(subject, "test", [traveler_request.traveler.email,"moghrabi@gmail.com"])

	return HttpResponseRedirect("/dashboard/#excursionoffers")



def feedback(request):
	"""Feedback view"""

	if request.method == 'GET':
		feedback_form = FeedbackForm()
		
	else:
		feedback_form = FeedbackForm(data = request.POST)

		if feedback_form.is_valid():
			subject = feedback_form.cleaned_data['subject']
			Your_Email_Address = feedback_form.cleaned_data['Your_Email_Address']
			message = feedback_form.cleaned_data['message']
			message = message + ". Wonderful client's email is: " + Your_Email_Address
			send_me_email("NEW FEEDBACK!!!!!! | excurj." , message, ['moghrabi@gmail.com'])
			return thankyou(request)

	return render(request, "excurj/feedback_email.html", {'feedback_form': feedback_form})

def thankyou(request):
	"""to show animation after submitting feedback and signing up for a new account"""
	return render(request, "excurj/thankyousvg/index.html", {})


