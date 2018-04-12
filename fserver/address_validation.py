

import requests

class AddressValidator():

	geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
	key = 'AIzaSyASh_MzDRPXhWA2VlhANyBA5cPYJcOyOA4'

	def __init__(self):
		self.address = None;
		self.lat = None;
		self.lng = None;


	def is_valid_address(self, address):
		print address
		geocode_request = self.request_geocode(address)
		if geocode_request is not None:
			return self.process_request(geocode_request)
		return False

	def request_geocode(self, address):
		print 'input --- ' + address
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
			
			# TODO - increase address validation complexity
			addr_components = req_js['results'][0]['address_components']
			for comps in addr_components:
				print comps
				if comps['types'][0] == 'postal_code':
					if not comps['short_name'] == '95112':
						print 'Invalid zipcode'
						#return False
			self.address =  req_js['results'][0]['formatted_address']
		return True



