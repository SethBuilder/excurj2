import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excurj_proj.settings')

import django
django.setup()

#to retrieve city ID and photo reference from Google Places API
import urllib.request, json

#to create a City object and save it in the database
from excurj.models import City

#for city images
from django.core.files import File
import requests

#to pull wiki summary for each city
import wikipedia

#to avoid connection errors from requests lib
from time import sleep


def populate_cities():
	#these cities will be highlighted on front page
	city_names = ['London', 'Paris', 'Munich', 'Miami', 'Tokyo', 'Beijing', 'Toronto', 'Barcelona', 'Budapest', 'Dubai', 'Vancouver' ]
	countries = ['England', 'France', 'Germany', 'USA', 'Japan', 'China', 'Canada', 'Spain', 'Hungary', 'UAE', 'Canada']

	#this will be returned at the end
	cities = []

	# GoogleKey = 'AIzaSyDaa7NZzS-SE4JW3J-7TaA1v1Y5aWUTiyc'
	# GoogleKey = 'AIzaSyDViGwJgWL18QSKvPozvAiqloyy1pW2lxg'
	GoogleKey = 'AIzaSyB1E9CZaaaw1c77A7eZSophK_LnaGX5XRQ'

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

		#extract city photo reference that we'll send to google places photo API
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
			try:
				#get the image
				retrieved_image = requests.get(city_image_url)
				sleep(5)#sleep to avoid too many requests in short period of time
			except requests.exceptions.ConnectionError as e:
				e.status_code = 'Connection refused from the Google API'

			#create local file to save remote image
			with open(city_names[i] + '.jpg', 'wb') as f:
				#write the remote image to the local file we just created
				f.write(retrieved_image.content)

				#open the local file with the image inside it
				with open(city_names[i] + '.jpg', 'rb') as reopen:
					#convert it to a Django File
					django_file = File(reopen)
					#save it to the ImageField -> args are: 1. the name of the file that is to be saved in MEDIA_ROOT path 2. The Django file itself 3. save instance
					if not created_city.city_image or not os.path.isfile("media/city_pictures/"+city_names[i] + '.jpg'):#if ImageField is empty then save image
						created_city.city_image.save(city_names[i] + '.jpg', django_file, save=True)
				


		created_city.save()# save City object
		
		cities.append(created_city)

		
	#delete local files as
	for city in cities:
		if os.path.isfile(city.name + '.jpg'):
			os.remove(city.name + '.jpg')
			print("removed local file: "+city.name)

	return cities#return a list of City objects

if __name__ == '__main__':
	print('starting populate.py')
	populate_cities()