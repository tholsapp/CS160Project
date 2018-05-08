

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
		zipcode_detected = False
		if request is not None:
			req_js = request.json()
			addr_components = req_js['results'][0]['address_components']
			for comps in addr_components:
				if comps['types'][0] == 'postal_code':
					zipcode_detected = True
					if not Zipcode.query.filter_by(zipcode=comps['long_name']).first():
						return False

			if not zipcode_detected:
				print "zipcode was not detected"
				return False
			# passed validation, store internal values
			self.address =  req_js['results'][0]['formatted_address']
			print "made it to the end"
			return True



