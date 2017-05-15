# import urllib.request, json
# def populate():

# 	city_names = ['London', 'Paris', 'Berlin', 'NYC', 'Tokyo', 'HK', 'RDJ', 'Barcelona', 'Budapest', 'Dubai' ]
# 	countries = ['England', 'France', 'Germany', 'USA', 'Japan', 'China', 'Brazil', 'Spain', 'Hungary', 'UAE']

# 	cities = []
# 	GoogleKey = 'AIzaSyDaa7NZzS-SE4JW3J-7TaA1v1Y5aWUTiyc'

# 	for i in range(len(city_names)):
# 		query = city_names[i] + "+" + countries[i] 
		
# 		url = ('https://maps.googleapis.com/maps/api/place/textsearch/json'
# 			'?query=%s'
# 			'&key=%s') % (query, GoogleKey)

# 		#grabbing the JSON results
# 		with urllib.request.urlopen(url) as response:
# 			jsonraw = response.read()
# 			jsondata = json.loads(jsonraw)
# 			print (jsondata['results'][0]['photos'][0]['photo_reference'])
# 			open("seif.txt", 'w+')

# populate()
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excurj_proj.settings')
import django
django.setup()

# from excurj.models import Reference, Request, User

# def test():

# 	reqs = Request.objects.filter(local_approval=True).order_by('-date')[:2]

# 	for i in range(len(reqs)):
# 		local_references_traveler = Reference.objects.filter(fun=True, author=reqs[i].local, referenced=reqs[i].traveler).latest()
# 		traveler_references_local = Reference.objects.filter(fun=True, author=reqs[i].traveler, referenced=reqs[i].local).latest()
# 		r = "req" + str(i)
# 		context_dict={r: {r : reqs[i], 
# 		'local_references_traveler' : local_references_traveler, 'traveler_references_local' : traveler_references_local}}
# 		print(context_dict)


# 	# for req in reqs:

# 	# 	print(req.id)
# 	# 	refs_loc = Reference.objects.filter(fun=True, author=req.local, referenced=req.traveler).latest()
# 	# 	refs_trav = Reference.objects.filter(fun=True, author=req.traveler, referenced=req.local).latest()

# 	# 	print(refs_loc, refs_trav)

from instagram.client import InstagramAPI
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'local':
    try:
        from test_settings import *

        InstagramAPI.host = test_host
        InstagramAPI.base_path = test_base_path
        InstagramAPI.access_token_field = "access_token"
        InstagramAPI.authorize_url = test_authorize_url
        InstagramAPI.access_token_url = test_access_token_url
        InstagramAPI.protocol = test_protocol
    except Exception:
        pass

# Fix Python 2.x.
try:
    import __builtin__
    input = getattr(__builtin__, 'raw_input')
except (ImportError, AttributeError):
    pass

client_id = input("Client ID: ").strip()
client_secret = input("Client Secret: ").strip()
redirect_uri = input("Redirect URI: ").strip()
raw_scope = input("Requested scope (separated by spaces, blank for just basic read): ").strip()
scope = raw_scope.split(' ')
# For basic, API seems to need to be set explicitly
if not scope or scope == [""]:
    scope = ["basic"]

api = InstagramAPI(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
redirect_uri = api.get_authorize_login_url(scope = scope)

print ("Visit this page and authorize access in your browser: "+ redirect_uri)

code = (str(input("Paste in code in query string after redirect: ").strip()))

access_token = api.exchange_code_for_access_token(code)
print ("access token: " )
print (access_token)

if __name__ == '__main__':
	test()