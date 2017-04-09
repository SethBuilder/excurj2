import urllib.request, json
def populate():

	city_names = ['London', 'Paris', 'Berlin', 'NYC', 'Tokyo', 'HK', 'RDJ', 'Barcelona', 'Budapest', 'Dubai' ]
	countries = ['England', 'France', 'Germany', 'USA', 'Japan', 'China', 'Brazil', 'Spain', 'Hungary', 'UAE']

	cities = []
	GoogleKey = 'AIzaSyDaa7NZzS-SE4JW3J-7TaA1v1Y5aWUTiyc'

	for i in range(len(city_names)):
		query = city_names[i] + "+" + countries[i] 
		
		url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
			'?query=%s'
			'&key=%s') % (query, GoogleKey)

		#grabbing the JSON results
		with urllib.request.urlopen(url) as response:
			jsonraw = response.read()
			jsondata = json.loads(jsonraw)
			print (jsondata['results'][0]['photos'][0]['photo_reference'])
			open("seif.txt", 'w+')

populate()