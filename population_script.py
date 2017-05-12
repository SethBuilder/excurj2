import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excurj_proj.settings')
import django
django.setup()
import urllib.request, json
from excurj.models import City, UserProfile, Excursion, Offer, Request, Reference
from django.contrib.auth.models import User
from django.core.files import File
import requests
import wikipedia
from time import sleep
import datetime
import glob
import random



def get_json(url):
	""" takes API URL and returns raw JSON response as image"""
	with urllib.request.urlopen(url) as response:
		jsonraw = response.read().decode()
		jsondata = json.loads(jsonraw)
		return jsondata

def populate_cities():
	""" populates City objects """
	#these cities will be highlighted on front page
	city_names = ['London', 'Paris', 'Munich', 'Miami', 'Beijing', 'Toronto', 'Barcelona', 'Budapest', 'Dubai', 'Vancouver' ]
	countries = ['England', 'France', 'Germany', 'USA', 'China', 'Canada', 'Spain', 'Hungary', 'UAE', 'Canada']

	#this will be returned at the end
	cities = []

	# GoogleKey = 'AIzaSyDaa7NZzS-SE4JW3J-7TaA1v1Y5aWUTiyc'
	GoogleKey = 'AIzaSyDViGwJgWL18QSKvPozvAiqloyy1pW2lxg'
	# GoogleKey = 'AIzaSyB1E9CZaaaw1c77A7eZSophK_LnaGX5XRQ'

	#only call the Google API if there are no City objects or no city pictures (db is empty)
	if City.objects.all().count() == 0 or len(glob.glob('media/city_images/*.jpg')) == 0:
		for i in range(len(city_names)):
			query = city_names[i] + "+" + countries[i] # to be sent to the Google Places API
			
			url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
				'?query=%s'
				'&key=%s') % (query, GoogleKey)

			#grabbing the JSON results
			with urllib.request.urlopen(url) as response:
				jsonraw = response.read()
				jsondata = json.loads(jsonraw)

			#now we'll use json results to extract city ID and city image
			city_id = jsondata['results'][0]['id']

			#create a City object
			created_city = City.objects.get_or_create(city_id=city_id)[0]

			#save name, country, description
			created_city.name = city_names[i]
			created_city.country = countries[i]

			# send city and country name to wikipedia and exctract first 5 sentences
			created_city.description = wikipedia.summary(city_names[i] + ' ' + countries[i]) 

			#extract city's 'photo reference' that we'll send to google places photo API
			city_image_ref = jsondata['results'][0]['photos'][0]['photo_reference']

			#set max width / can be changed if front end requires it
			maxwidth = '400'

			#The URL the HTTP Response to which brings the image
			city_image_url = ('https://maps.googleapis.com/maps/api/place/photo'
			'?maxwidth=%s'
			'&photoreference=%s'
			'&key=%s') % (maxwidth, city_image_ref, GoogleKey)

			#check if the image exists already
			if not os.path.isfile("media/city_pictures/"+city_names[i] + '.jpg'):

				#only get the remote image if the file is not there
				django_file = save_image(city_image_url, city_names[i] + '.jpg')

				#if ImageField is empty then save image
				if not created_city.city_image or not os.path.isfile("media/city_pictures/"+city_names[i] + '.jpg'):
					created_city.city_image.save(city_names[i] + '.jpg', django_file, save=True)
					django_file.close()
				


			created_city.save()# save City object in db
			
			cities.append(created_city)

	else:
		cities = City.objects.all()

		
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
	urls = ['https://randomuser.me/api/?nat=gb&results=1', 'https://randomuser.me/api/?nat=fr&results=2', 
	'https://randomuser.me/api/?nat=de&results=1', 'https://randomuser.me/api/?nat=us&results=2', 
	'https://randomuser.me/api/?results=0', 'https://randomuser.me/api/?results=1', 'https://randomuser.me/api/?results=2&nat=es', 
	'https://randomuser.me/api/?results=1', 'https://randomuser.me/api/?results=0', 'https://randomuser.me/api/?results=1&nat=ca']

	#go through random data urls
	for i in range(len(urls)):
		users_in_json = get_json(urls[i])#bring json data for users of specific city and nationality
		user_list = get_users(users_in_json)#returns list of User objects
		#send User objects list, json data and a City object to create profiles
		user_profiles = get_profiles(user_list, cities[i], users_in_json)
	
def get_users(users):
	"""takes JSON data for test users and bring back a list of User objects"""
	user_list = []
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

		user.save()#save User object
		user_list.append(user)

	return user_list

def get_profiles(user_list, city, users_in_json):
	profiles = []
	for i in range(len(user_list)):

		#now create User Profile
		profile = UserProfile.objects.get_or_create(user=user_list[i])[0]

		#fill in the City object
		profile.city = city
		profile.dob = datetime.datetime.strptime(users_in_json['results'][i]['dob'], '%Y-%m-%d %H:%M:%S').date()
		# print(users_in_json['results'][i]['dob'])
		# print(users_in_json['results'][i]['picture']['large'])# TO DELETE

		#fetch Django file (prof_pic)
		django_file = save_image(users_in_json['results'][i]['picture']['large'], str(profile.user.id) + '.jpg')

		#save prof_pic
		profile.prof_pic.save(str(profile.user.id) + '.jpg', django_file, save=True)
		django_file.close()

		#fill gender
		profile.sex = users_in_json['results'][i]['gender']

		profile.save()
		profiles.append(profile)

	#delete local files (prof pics) as they're already uploaded to media root
	for profile in profiles:
		if os.path.isfile(str(profile.user.id) + '.jpg'):
			os.remove(str(profile.user.id) + '.jpg')
			print("removed local file: "+ str(profile.user.id))


def save_image(url, file_name):
	""" pulls an image from a URL and returns a Django File """

	#retrieve the profile pic
	try:
		retrieved_image = requests.get(url)
		sleep(2)

	except requests.exceptions.ConnectionError as e:
		e.status_code = 'Connection refused from random API'

	#create local file to save remote image
	with open(file_name, 'wb') as f:
		#write the remote image to the local file we just created
		f.write(retrieved_image.content)

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
		msg1 = "Hey awesome people of " + city.name + "!" + " I'm arriving in your city quit soon and would love to meet some of you!"
		msg2 = "I'm visiting " + city.name + " with a friend quit soon! we're nice and friendly and would love to meet up!"
		msg3 = "Hello, Hello, I'm solo traveling around the world and soon to arrive in " + city.name + "!" + " would love to meet you some locals, maybe to walk around town and have lunch or dinner, Ciao, Ciao and talk to you soon!! :)"

		messages.extend((msg3,msg2, msg1))

	# #generate a random date from today till last day of the year
	# start_date = datetime.date.today().toordinal()
	# end_date = datetime.date.today().replace(day=31, month=12).toordinal()

	#generate 10 excursions
	for i in range(10):
		#generate random date
	 	# date = datetime.date.fromordinal(random.randint(start_date, end_date))

	 	#create Excursion object
	 	excursion = Excursion(traveler=random.choice(user_list), 
	 		city=random.choice(city_list), message=random.choice(messages), date=generate_date() )

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
	for i in range(10):
		request = Request(traveler=random.choice(user_list), local=random.choice(user_list), 
			message=random.choice(messages), date=generate_date(), local_approval=random.choice([True, False]))

		request.save()
		requests.append(request)

	return requests

def populate_references():
	""" populating references """

	user_list = User.objects.all()

	messages=[]
	references=[]

	for user in user_list:
		msg1 = "I had so much fun with %s! we ended up pub crawling at midnight. Such a great time it was!" 
		msg2 = "%s was so nice and interesting, we walked around art museums together and had interesting conversations about the the contemporary art scenes in our countries." 
		msg3 = "%s showed me around town and seemed to know so many interesting things!" 

		messages.extend((msg3,msg2, msg1))

	for i in range(10):
		referenced=random.choice(user_list)
		description=random.choice(messages) % referenced.first_name.title()
		reference = Reference(author=random.choice(user_list), referenced=referenced, description=description, fun=True)
		reference.save()
		references.append(reference)

	return references

if __name__ == '__main__':
	print('starting populate.py')
	# populate_cities()
	populate_users()
	populate_excursions()
	populate_offers()
	populate_requests()
	populate_references()

