import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excurj_proj.settings')
import django
django.setup()
import urllib.request, json
from excurj.models import City, UserProfile, Excursion, Request, RequestReference
from django.contrib.auth.models import User
from django.core.files import File
import requests
import wikipedia
from time import sleep
import datetime
import glob
import random
from django.http import HttpResponseServerError
from django.contrib.staticfiles.storage import staticfiles_storage
import csv

def get_json(url):
	"""
		takes Google Places api url and returns raw JSON response
	 	of random users of different nationalities
	 """
	with urllib.request.urlopen(url) as response:
		jsonraw = response.read().decode()
		jsondata = json.loads(jsonraw)
		return jsondata

def get_csv(url):
	"""
		takes url that returns all world cities
	 """
	with urllib.request.urlopen(url) as response:
		jsonraw = response.read().decode()
		return jsonraw

def get_google_key():
	""" returns Google api key"""

	GoogleKey = ''

	return GoogleKey

def get_city_json(query):
	"""takes city search query and return JSON city data as per Google Places API"""

	url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
				'?query=%s'
				'&key=%s') % (query, get_google_key())

	try:
		#grabbing the JSON results
		response = requests.get(url)
		jsondata = json.loads(response.text)
		print(jsondata)
		return jsondata

	except IndexError:
		return -1

def populate_city(city_id, query):
	""" takes city ID (as per Google Places API) and search query (from the homepage search field)
	returns City object """

	#create a City object
	if City.objects.filter(city_id=city_id).exists():
	    created_city = City.objects.filter(city_id=city_id)[0]
	else:
	    created_city = City.objects.create(city_id=city_id)

	#save name, country, description
	created_city.name = query#Save search query as city name
	created_city.slug = query.replace(", ", "-").replace(' ', '-').lower()#replaces spaces and commas with -

	# send search query to wikipedia and exctract first 5 sentences
	try:
		created_city.description = wikipedia.summary(query)
		if created_city.description == "":
			created_city.description = "We couldn't find wiki summary for this town."
	except wikipedia.exceptions.PageError:
		created_city.description = "We couldn't find wiki summary for this town."
	except wikipedia.exceptions.DisambiguationError:
		created_city.description = "We couldn't find wiki summary for this town."

	#extract city data as per Google Places API
	jsondata = get_city_json(query)

	#Extract lat and lng
	created_city.lat = jsondata['results'][0]['geometry']['location']['lat']
	created_city.lng = jsondata['results'][0]['geometry']['location']['lng']

	#extract city's 'photo reference' that we'll send to google places photo API
	city_image_ref = jsondata['results'][0]['photos'][0]['photo_reference']

	#set max width / can be changed if front end requires it
	maxwidth = '1600'

	#The URL the HTTP Response to which brings the image
	city_image_url = ('https://maps.googleapis.com/maps/api/place/photo'
	'?maxwidth=%s'
	'&photoreference=%s'
	'&key=%s') % (maxwidth, city_image_ref, get_google_key())

	#check if the image exists already
	if not os.path.isfile("media/city_pictures/"+ created_city.slug + '.jpg'):

		#only get the remote image if the file is not there
		django_file = save_image(city_image_url, created_city.slug + '.jpg')

		#if ImageField is empty then save image
		if not created_city.city_image or not os.path.isfile("media/city_pictures/"+created_city.slug + '.jpg'):
			created_city.city_image.save(created_city.slug + '.jpg', django_file, save=True)
			django_file.close()

	created_city.save()# save City object in db

	#delete local files as they're already uploaded to media root
	if os.path.isfile(created_city.slug + '.jpg'):
		os.remove(created_city.slug + '.jpg')

	return created_city

def populate_cities():
	""" populates City objects """
	#these cities will be highlighted on front page
	city_names = ['London', 'Paris', 'Munich', 'New York City', 'Beijing', 'Toronto', 'Barcelona', 'Budapest', 'Dubai', 'Vancouver',
	'Hong Kong',
	'Singapore',
	'Bangkok',
	'Macau',
	'Shenzhen',
	'Kuala Lumpur',
	'Antalya',
	'Istanbul',
	'Seoul',
	'Rome',
	'Phuket',
	'Guangzhou',
	'Mecca',
	'Pattaya',
	'Taipei',
	'Miami',
	'Prague',
	'Shanghai',
	'Las Vegas',
	'Milan',
	'Moscow',
	'Amsterdam',
	'Vienna',
	'Venice',
	'Los Angeles',
	'Lima',
	'Tokyo',
	'Johannesburg',
	'Sofia',
	'Orlando',
	'Berlin',
	'Ho Chi Minh City',
	'Florence',
	'Madrid',
	'Warsaw',
	'Doha',
	'Nairobi',
	'Delhi',
	'Mumbai',
	'Chennai',
	'Mexico City',
	'Dublin',
	'San Francisco'
	]
	countries = ['England', 'France', 'Germany', 'USA', 'China', 'Canada', 'Spain', 'Hungary', 'UAE', 'Canada',
	'China',
	'Singapore',
	'Thailand',
	'China',
	'China',
	'Malaysia',
	'Turkey',
	'Turkey',
	'South Korea',
	'Italy',
	'Thailand',
	'China',
	'Saudi Arabia',
	'Thailand',
	'Taiwan',
	'USA',
	'Czech Republic',
	'China',
	'USA',
	'Italy',
	'Russia',
	'Netherlands',
	'Austria',
	'Italy',
	'USA',
	'Peru',
	'Japan',
	'South Africa',
	'Bulgaria',
	'USA',
	'Germany',
	'Vietnam',
	'Italy',
	'Spain',
	'Poland',
	'Qatar',
	'Kenya',
	'India',
	'India',
	'India',
	'Mexico',
	'Ireland',
	'USA'
]

	# world_cities = get_csv('https://pkgstore.datahub.io/core/world-cities/world-cities_csv/data/6cc66692f0e82b18216a48443b6b95da/world-cities_csv.csv');
	# with open('world_cities.csv', encoding="utf8") as f:
	# 	reader = csv.reader(f)
	# 	world_cities = list(reader)
		# print(world_cities[12])

	#this will be returned at the end
	cities = []

	#only call the Google API if there are no City objects or no city pictures (db is empty)
	# if not City.objects.all() or len(glob.glob('media/city_images/*.jpg')) == 0:

	for i in range(len(city_names)):
		# query = world_cities[i+1] # to be sent to the Google Places API
		query = city_names[i] + ", " + countries[i]
		try:
			#now we'll use json results to extract city ID and city image
			city_id =  get_city_json(query)['results'][0]['id']
			created_city = populate_city(city_id, query)
			if created_city.name=='' or created_city.lng==None or created_city.lat==None:
				created_city.delete()
			else:
			    created_city.save()
			    cities.append(created_city)
		except Exception as e:
			pass

	#If there are cities, just pull them
	# else:
	# 	cities = City.objects.all()


	#delete local files as they're already uploaded to media root
	for city in cities:
		if os.path.isfile(city.name + '.jpg'):
			os.remove(city.name + '.jpg')
			print("removed local file: "+city.name)

	return cities#return a list of City objects

def populate_users():
	""" populates User and UserProfile objects """

	#have a list of City objects at hand
	#if there's no City objects or no pics
	if City.objects.all().count() == 0 or len(glob.glob('media/city_images/*.jpg')) == 0:
		cities = populate_cities()#call the function
	else:
		cities = City.objects.all()#else, call them from the db

	#URLs that bring back data for test users, one URL for each city
	urls = ['https://randomuser.me/api/?nat=gb&results=5', 'https://randomuser.me/api/?nat=fr&results=4',
	'https://randomuser.me/api/?nat=de&results=3', 'https://randomuser.me/api/?nat=us&results=0',
	'https://randomuser.me/api/?results=0', 'https://randomuser.me/api/?results=1', 'https://randomuser.me/api/?results=7&nat=es',
	'https://randomuser.me/api/?results=0',
	'https://randomuser.me/api/?results=0',
	'https://randomuser.me/api/?results=3&nat=ca',
	'https://randomuser.me/api/?nat=gb&results=2',
	'https://randomuser.me/api/?nat=gb&results=10',
	'https://randomuser.me/api/?nat=gb&results=5',
	'https://randomuser.me/api/?nat=gb&results=3',
	'https://randomuser.me/api/?nat=gb&results=5',
	'https://randomuser.me/api/?nat=gb&results=20',
# 	'https://randomuser.me/api/?nat=gb&results=5',
# 	'https://randomuser.me/api/?nat=gb&results=5',
# 	'https://randomuser.me/api/?nat=gb&results=2',
# 	'https://randomuser.me/api/?nat=gb&results=5',
# 	'https://randomuser.me/api/?nat=gb&results=2',
# 	'https://randomuser.me/api/?nat=gb&results=5',
# 	'https://randomuser.me/api/?nat=gb&results=5',
# 	'https://randomuser.me/api/?nat=gb&results=1',
# 	'https://randomuser.me/api/?nat=gb&results=5',
# 	'https://randomuser.me/api/?nat=gb&results=5',
# 	'https://randomuser.me/api/?nat=gb&results=3',
# 	'https://randomuser.me/api/?nat=gb&results=8'
	]

	#go through random data urls
	for i in range(len(urls)):

		#bring random json data for users of specific city and nationality
		users_in_json = get_json(urls[i])

		#send User objects list, json data and a City object to create profiles
		user_list = get_users(users_in_json, cities[i], users_in_json)#returns list of User objects

		# user_profiles = get_profiles(user_list, cities[i], users_in_json)

def get_users(users, city, users_in_json):
	"""takes JSON data for test users and bring back a list of User and UserProfile objects"""

	user_list = []
	profiles = []

	#go thru all users returned from the random user API
	for i in range(len(users['results'])):

		#1. fetch username
		username = users['results'][i]['login']['username']

		#create User object
		user = User.objects.get_or_create(username=username)[0]

		#now fill in first name, last name, email, password
		user.first_name = users['results'][i]['name']['first']
		user.last_name = users['results'][i]['name']['last']
		user.email = users['results'][i]['email']
		user.password = users['results'][i]['login']['password']


		#now create User Profile
		profile = UserProfile.objects.get_or_create(user=user)[0]

		#fill in the City object
		profile.city = city
		profile.dob = datetime.datetime.strptime(users_in_json['results'][i]['dob'], '%Y-%m-%d %H:%M:%S').date()

		#fetch Django file (prof_pic)
		django_file = save_image(users_in_json['results'][i]['picture']['large'], str(profile.user.id) + '.jpg')

		#save prof_pic
		profile.prof_pic.save(str(profile.user.id) + '.jpg', django_file, save=True)
		django_file.close()

		#fill gender
		profile.sex = users_in_json['results'][i]['gender']

		#now fill education and career

		education = ["MBA", 'MSc Physics', 'BSc ComSi', 'Bachelor of Sociology', 'Bachelor of Latin and Italian',
		'Student of the Arts!', 'MA', 'High School Diploma', 'PhD of Astronomy', 'Community College',
		'Chemical Engineering', 'English Literature']

		career = ['CEO', 'student', 'web developer', 'teacher', 'interpreter', 'curator', 'teacher', 'shop keeper',
		'professor', 'Policeman', 'Librarian']

		profile.career = random.choice(career)
		profile.education = random.choice(education)

		profile.save()
		profiles.append(profile)

		user.save()#save User object
		user_list.append(user)



	#delete local files (prof pics) as they're already uploaded to media root
	for profile in profiles:
		if os.path.isfile(str(profile.user.id) + '.jpg'):
			os.remove(str(profile.user.id) + '.jpg')
			print("removed local file: "+ str(profile.user.id))

	return user_list


def save_image(url, file_name):
	""" pulls an image from a URL and returns a Django File """

	#retrieve the profile pic
	try:
		retrieved_image = requests.get(url)
		sleep(3)#To avoid jamming the requests library
		image = retrieved_image.content

	except requests.exceptions.ConnectionError as e:
		e.status_code = 'Connection refused'
		print(e.status_code)

		#If requests throws exception use this alternative city image
		retrieved_image = open('/home/excurj/excurj_proj/static/images/one.jpg', 'rb').read()
		image = retrieved_image

	#create local file to save remote image
	with open(file_name, 'wb') as f:
		#write the remote image to the local file we just created
		f.write(image)

	reopen = open(file_name, 'rb')
	django_file = File(reopen)

	return django_file

def populate_excursions():

	""" travelers list excursions they wish to have by listing a city (destination) and a message.
		For example: "Hey great people of London!, coming your way, would love to meet up with some of you!!"
	 """
	excursions = []

	#prepare a list of all User objects
	user_list = User.objects.all()

	#prepare a list of all City objects
	city_list = City.objects.all()

	#prepare a list of possible messages
	messages = []

	#populate messages travelers put on their excursions
	for city in city_list:
		msg1 = "Hey awesome people of %s. I'm arriving in your city quit soon and would love to meet some of you!"
		msg2 = "I'm visiting %s with a friend quit soon! we're nice and friendly and would love to meet up!"
		msg3 = "Hello, Hello, I'm solo traveling around the world and soon to arrive in %s! would love to meet you some locals, maybe to walk around town and have lunch or dinner, Ciao, Ciao and talk to you soon!! :)"
		msg4 = "I'll arrive in %s in couple of weeks, would love to meet up."
		msg5 = "Hello %s! I'm arriving over the holidays with my Aunt. Would love to say hello."
		msg6 = "Hey. I'm coming to %s for the first time soon, would love to make friends there!"
		msg7 = "Hey. I'm arriving in %s with my partner soon, would love some nice people!"
		msg8 = "Hello! I'm coming to %s soon, I'm a nice friendly person who loves to chat!"
		msg9 = "I'm coming to %s with my family, anyone like to show us around? thanks! :)"

		messages.extend((msg3,msg2,msg1,msg4, msg5, msg6, msg7, msg8, msg9))


	#generate 10 excursions
	for i in range(35):
		#generate random date
	 	# date = datetime.date.fromordinal(random.randint(start_date, end_date))
	 	city=random.choice(city_list)
	 	message=random.choice(messages) % city.display_name

	 	#create Excursion object
	 	excursion = Excursion(traveler=random.choice(user_list),
	 		city=city, message=message, date=generate_date() )

	 	excursion.save()
	 	excursions.append(excursion)

	return excursions

def generate_date():
	""" generate a date between today and the end of the year """

	#generate a random date from today till last day of the year
	start_date = datetime.date.today().toordinal()
	end_date = datetime.date.today().replace(day=31, month=12).toordinal()
	date = datetime.date.fromordinal(random.randint(start_date, end_date))

	return date


def populate_offers():
	""" populates offers made by locals to travelers coming to their city """
	#first, prepare a list of all users
	user_list = User.objects.all()

	#then, prepare a list of all excursions
	excursion_list = Excursion.objects.all()

	#messages list
	messages = []

	offers=[]

	#populate messages travelers put on their excursions
	for excurj in excursion_list:
		msg1 = "Hey there! nice to meet you. I see you're coming to %s, would love to meet up and show you around my hometown."
		msg2 = "Hey! my name is Sammy and would like to show you around %s and maybe meet up with my friends at the club, let me know if that works!"
		msg3 = "Ciao, Ciao! maybe I can go out with you tonight and introduce you to the best clubs around %s!"

		messages.extend((msg3,msg2, msg1))

	#generate 10 offers
	for i in range(10):
		trip=random.choice(excursion_list)
		message = random.choice(messages) % (trip.city.name)
		offer = Offer(local=random.choice(user_list), message=message, trip=trip,
			traveler_approval = random.choice([True, False]))
		offer.save()
		offers.append(offer)

	return offers

def populate_requests():
	""" populate requests for when a traveler asks local to take him out upon liking his profile """
	user_list = User.objects.all()
	messages=[]
	requests=[]
	excursion_list = Excursion.objects.all()

	#populate messages travelers put on their excursions
	for excurj in excursion_list:
		msg1 = "Hi! I'm coming to %s this month and I like your profile! would you want to take me out on a Saturday?" % excurj.city.name
		msg2 = "Hi! I'm coming to %s over Christams, I'm available on Friday, do you wanna meet up?" % excurj.city.name
		msg3 = "Ciao, Ciao! can I go out with you this weekend? leaving %s on Monday :( :D" % excurj.city.name

		messages.extend((msg3,msg2, msg1))

	#generate 10 requests
	for i in range(100):
		traveler=random.choice(user_list)
		local=random.choice(user_list)

		if traveler != local:
			request = Request(traveler=traveler, local=local,
				message=random.choice(messages), date=generate_date())

			traveler_already_left_ref_for_local = False

			for r in requests:
				if request.traveler != r.traveler:
					continue
				else:
					traveler_already_left_ref_for_local = True
					break

		if traveler_already_left_ref_for_local == False:
			request.save()
			requests.append(request)

	return requests

def populate_request_references():
	""" Traveler request local to take her out.
	After they meet they leave each other a reference. """

	user_list = User.objects.all()
	req_list = populate_requests()

	messages_from_travelers=[]
	messages_from_locals=[]
	references=[]

	for user in user_list:
		msg_from_traveler1 = "Thank you %s for a wonderful time! You're more than welcome to visit me anytime."
		msg_from_traveler2 = "%s was so nice and interesting, we walked around art museums together and had interesting conversations."
		msg_from_traveler3 = "%s showed me around town and seemed to know so many interesting things!"
		msg_from_traveler4 = "As an avid traveler I immensely enjoy meeting friendly locals. Thank you %s please do stop by."
		msg_from_traveler5 = "Thank you %s! I enjoyed the tour!"
		msg_from_traveler6 = "Couldn't have asked for a better guide than %s. Such a great persoanlity!"
		msg_from_traveler7 = "%s is a wonderful guide and now a true friend."
		msg_from_traveler8 = "I had an enjoyable time with %s!"
		msg_from_traveler9 = "%s showed me around town and visited attractions. It was a wonderful time except wasn't for the rain :)"

		msg_from_local1 = "I met up with %s and walked around town, then we had lunch and tried the local coffee, we'll stay in touch for sure."
		msg_from_local2 = "%s was so curious about town and I enjoyed explaining all the small details that I thought would be interesting "
		msg_from_local3 = "%s is cool! we'll meet up again in the future."
		msg_from_local4 = "%s is an interesting person and quit well-travlled. I enjoyed showing him around my town."
		msg_from_local5 = "Thank you %s for visiting me! come back anytime!"
		msg_from_local6 = "%s is a wonderful traveller, full of curiousity and awesomeness!"
		msg_from_local7 = "%s was a curious traveler that I enjoyed showing him around"
		msg_from_local8 = "I enjoyed the company of %s, you're welcome to visit me again anytime!"
		msg_from_local9 = "%s is now my friend that I'd love to visit back!"



		messages_from_travelers.extend((msg_from_traveler1,msg_from_traveler2, msg_from_traveler3, msg_from_traveler4,msg_from_traveler5, msg_from_traveler6 ))
		messages_from_locals.extend((msg_from_local1,msg_from_local2, msg_from_local3, msg_from_local4, msg_from_local5, msg_from_local6))

	for req in req_list:

		traveler_desc = random.choice(messages_from_travelers) % req.local.first_name.title()
		local_desc = random.choice(messages_from_locals) % req.traveler.first_name.title()

		request_reference = RequestReference(request=req, traveler_desc=traveler_desc,
			local_desc = local_desc, traveler_fun=True, local_fun=True)

		request_reference.save()
		references.append(request_reference)

	return references

if __name__ == '__main__':
	print('starting populate.py')
	# populate_cities()
	populate_users()
	populate_excursions()
	# populate_offers()
	populate_request_references()
	#FINITO