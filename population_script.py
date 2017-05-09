import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excurj_proj.settings')
import django
django.setup()
import urllib.request, json
from excurj.models import City
from django.contrib.auth.models import User
from excurj.models import UserProfile
from django.core.files import File
import requests
import wikipedia
from time import sleep
import datetime
import glob


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

if __name__ == '__main__':
	print('starting populate.py')
	# populate_cities()
	populate_users()

