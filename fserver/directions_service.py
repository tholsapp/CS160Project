
import requests

class GMapDirectionService:

	def __init__(self, origin, destination):
		self.json_directions_response = self.make_directions_request(origin, destination)
		print self.json_directions_response
		self.origin = origin
		self.destination = destination
		self.overview_path = self.json_directions_response['routes'][0]['overview_polyline']['points']
		self.total_polylines = self.get_polylines(self.json_directions_response)
		self.total_duration = self.json_directions_response['routes'][0]['legs'][0]['duration']['value'];
		self.steps =  self.get_steps(self.json_directions_response)

	def make_directions_request(self, origin, destination):
		url = 'https://maps.googleapis.com/maps/api/directions/json'
		params = {
			'key' : 'AIzaSyASh_MzDRPXhWA2VlhANyBA5cPYJcOyOA4',
			'origin': origin,
			'destination' : destination
		}
		return requests.get(url, params=params).json()


	def get_steps(self, gmap_json_response):
		"""
		Sample step

		{u'html_instructions': u'Turn <b>left</b> onto <b>S 5th St</b><div style="font-size:0.9em">Destination will be on the left</div>', 
		u'distance': {u'text': u'0.2 mi', u'value': 325}, 
		u'travel_mode': u'DRIVING', u'maneuver': u'turn-left', 
		u'start_location': {u'lat': 37.3320448, u'lng': -121.8817666}, 
		u'polyline': {u'points': u'glzbF``|fV~GyEtE}C'}, 
		u'duration': {u'text': u'1 min', u'value': 81}, 
		u'end_location': {u'lat': 37.3295322, u'lng': -121.8798865}}
		"""
		step_list = []
		for legs in gmap_json_response['routes']:
			for step in legs['legs'][0]['steps']:
				step_list.append(step)
		return step_list

	# def get_duraction(self, gmap_json_response)
	def get_polylines(self, gmap_json_response):
		poly_list = []
		for legs in gmap_json_response['routes']:
			for step in legs['legs'][0]['steps']:
				poly_list.append(step)
		return poly_list



if __name__ == '__main__':
	obj = GMapDirectionService('1 Washington Sq, San Jose, CA 95192', '576 s. 5th st., san jose, ca 95112')
	print obj.total_duration
	print obj.overview_path