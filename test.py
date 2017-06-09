import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excurj_proj.settings')
import django
django.setup()
import urllib.request, json
def populate():

	city_names = ['London', 'Paris', 'Berlin', 'NYC', 'Tokyo', 'HK', 'RDJ', 'Barcelona', 'Budapest', 'Dubai' ]
	countries = ['England', 'France', 'Germany', 'USA', 'Japan', 'China', 'Brazil', 'Spain', 'Hungary', 'UAE']

	cities = []
	GoogleKey = 'AIzaSyDaa7NZzS-SE4JW3J-7TaA1v1Y5aWUTiyc'

	# for i in range(len(city_names)):
	# 	query = city_names[i] + "+" + countries[i] 
		
	# 	url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
	# 		'?query=%s'
	# 		'&key=%s') % (query, GoogleKey)

	# 	#grabbing the JSON results
	# 	with urllib.request.urlopen(url) as response:
	# 		jsonraw = response.read()
	# 		jsondata = json.loads(jsonraw)
			# print (jsondata['results'][0]['geometry']['location']['lat'])
			
	url = 'https://graph.facebook.com/search?q=amman,jordan&type=event&access_token=EAADuTyDZATeoBAIQokWxUwPWETSzcv8tRcN6eMAbRm5J4YPHUtD7BC7wZAqXzaAar750DZBNalKXG1TyJfMABkZBaL8MRaHbKZA3ifvpKiXrNACp9PZAlZAIeKu8MEejTB7a3DLciHZCpdWg0FfxTGhCHMGuk7iLBr4vzZB8wBzX5TUfcdFSBI31d1MbzmcZAUFA4ZD'

	with urllib.request.urlopen(url) as response:
		jsonraw = response.read()
		jsondata = json.loads(jsonraw)
		print(jsondata['data'][0]['description'])

# from excurj.models import Reference, Request, User

# def test():

# 	reqs = Request.objects.filter(traveler = local, local_approval=True).order_by('-date')[:2]

# 	for i in range(len(reqs)):
# 		local_references_traveler = Reference.objects.filter(fun=True, author=reqs[i].local, referenced=reqs[i].traveler).latest()
# 		traveler_references_local = Reference.objects.filter(fun=True, author=reqs[i].traveler, referenced=reqs[i].local).latest()
# 		r = "req" + str(i)
# 		context_dict={r: {r : reqs[i], 
# 		'local_references_traveler' : local_references_traveler, 'traveler_references_local' : traveler_references_local}}
# 		print(context_dict)


	# for req in reqs:

	# 	print(req.id)
	# 	refs_loc = Reference.objects.filter(fun=True, author=req.local, referenced=req.traveler).latest()
	# 	refs_trav = Reference.objects.filter(fun=True, author=req.traveler, referenced=req.local).latest()

	# 	print(refs_loc, refs_trav)
if __name__ == '__main__':
	# test()
	populate()