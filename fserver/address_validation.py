

from fserver.models import Zipcode
import requests

class AddressValidator():
	""" Helper class to validate addresses supplied by user 
	Enforces address to be within counties (San Mateo, Santa Clara, Alameda """

	geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
	key = 'AIzaSyASh_MzDRPXhWA2VlhANyBA5cPYJcOyOA4'

	def __init__(self):
		self.address = None
		self.lat = None
		self.lng = None


	def is_valid_address(self, address):
		geocode_request = self.request_geocode(address)
		if geocode_request is not None:
			return self.process_request(geocode_request)
		return False

	def request_geocode(self, address):
		params = {
		'address' : address,
		'key' : self.key,
		}
		# make geocode request
		req = requests.get(self.geocode_url, params=params)
		if req.status_code == 200:
			return req
		return None

	def process_request(self, request):
		if request is not None:
			req_js = request.json()
			zipcode = 95050 
			# get zipcode from request
			for comp in req_js['results'][0]['address_components']:
				if comp['types'][0] == 'postal_code':
				 	print comp['long_name']
				 	zipcode = comp['long_name']
			#print req_js['results'][0]['address_components'][-2]
			# for x in req_js:
			# 	print x
			# TODO - increase address validation complexity
			addr_components = req_js['results'][0]['address_components']
			for comps in addr_components:
				if comps['types'][0] == 'postal_code':
					# TODO add some kind of data to check if valid zip code (i.e. in the bay area)
					# if comps['short_name'] in MASTER ZIPCODE_DATABASE or ZIPCODE_LIST
					if not Zipcode.query.filter_by(zipcode=zipcode).first():
						return False


			# passed validation, store internal values
			self.address =  req_js['results'][0]['formatted_address']
		return True



