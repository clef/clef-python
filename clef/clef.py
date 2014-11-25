import requests
from requests.exceptions import RequestException 

CLEF_APP_ID ='4f318ac177a9391c2e0d221203725ffd'
CLEF_APP_SECRET = '2125d80f4583c52c46f8084bcc030c9b'

class ClefSetupError(Exception):
	""" Raised when there is something wrong with a user's credentials - Clef app_id or app_secret """
	pass

class ClefCodeError(Exception):
	""" Raised when something goes wrong with OAuth handshake and Clef is unable to exchange code for access token """
	pass

class ClefTokenError(Exception):
	""" Raised when Clef is unable to exchange the token for user information """
	pass 

class ClefServerError(Exception):
	""" Raised when Clef's servers are down """
	pass 

class ClefConnectionError(Exception):
	""" Raised when no network connection is detected """
	pass 

class ClefLogoutError(Exception):
	""" Raised when an application's logout hook does not match their domain or has not been configured right """
	pass 

class ClefNotFoundError(Exception):
	""" Raised when request to Clef API returns a 404 error """
	pass 

# Clef 403 error strings mapped to the right class of error to raise 
message_to_error_map = {
	'Invalid App Id.': ClefSetupError,
	'Invalid App Secret.': ClefSetupError,
	'Invalid OAuth Code.': ClefCodeError,
	'Invalid token.' : ClefTokenError,
}

def clef_error_check(func_to_decorate):
	""" A decorator for handling errors when making call to Clef API """
	def wrapper(*args, **kwargs):
		try:
			response = func_to_decorate(*args, **kwargs)
		except RequestException:
			raise ClefConnectionError('Clef encountered a network connectivity problem. Are you sure you are connected to the Internet?')
		else:
			raise_right_error(response)
		return response.json() # decode json  
	return wrapper 

def raise_right_error(response):
	""" If API call returns status code other than 200, raise the right kind of error """
	if response.status_code == 500:
		raise ClefServerError('Clef server is down right now')
	if response.status_code == 403:
		message = response.json().get('error')
		error_class = message_to_error_map[message]
		if error_class == ClefTokenError:
			message = 'Someething went wrong at Clef. We are unable to retrieve user information with this token.'
		raise error_class(message)
	if response.status_code == 400:
		raise ClefLogoutError(response.json().get('error'))
	if response.status_code == 404:
		raise ClefNotFoundError('Unable to retrieve the page. Are you sure the Clef api endpoint is configured right?')
	# maybe make this more explicit and only return when status code is 200? 
	return


class ClefAPI(object):
	def __init__(self, app_id, app_secret, root=None):
		if not root:
			root = 'https://clef.io/api'
		version = 'v1'
		self.api_key = app_id
		self.api_secret = app_secret 
		self.api_endpoint = '/'.join([root, version])
		self.authorize_url = '/'.join([self.api_endpoint, 'authorize'])
		self.info_url = '/'.join([self.api_endpoint, 'info'])

	@clef_error_check
	def _call(self, method, url, params):
		""" Makes request to Clef API. Decorator takes care of error handling """
		request_params = {}
		if method == 'get':
			request_params['params'] = params 
		elif method == 'post':
			request_params['data'] = params 
		response = requests.request(method, url, **request_params)
		return response 

	def get_user_info(self, code=None, access_token=None):
		""" Exchanges a code for an Oauth token, does the handshake and returns Clef user info """
		if access_token:
			return self._get_user_info(access_token)
		# need to do the handshake to get the token
		data = dict(code=code, app_id=self.api_key, app_secret=self.api_secret)
		token_response = self._call('post', self.authorize_url, params=data)
		# token_dict = token_response.json() # decode json
		access_token = token_response.get('access_token')
		# make a request with the token to get user details
		info_response = self._call('get', self.info_url, params={'access_token': access_token})
		# info_dict = info_response.json()
		user_info = info_response.get('info')
		return user_info 

	def _get_user_info(self, access_token):
		""" We already have a token and do not need to go through the handshake """
		# TODO: check to see if access tokens expire
		info_response = self._call('get', self.info_url, params={'access_token': access_token})
		# info_dict = info_response.json()
		user_info = info_response.get('info')
		return user_info







def callback():
	code = 'code_123456789'
	authorize_url = 'https://clef.io/api/v1/authorize'
	data = dict(code=code, app_id=CLEF_APP_ID, app_secret=CLEF_APP_SECRET)
	try:
		response = requests.post(authorize_url, data=data)
	except RequestException:
		raise ClefConnectionError('You have not established a connection')
	
	status_code = response.status_code

	# something went wrong with exchanging code for token
	if status_code == 403:
		response_object = response.json()
		message = response_object.get('error')
		if 'OAuth' in message:
			raise ClefCodeError(message)
		raise ClefSetupError(message)

	if status_code == 500:
		raise ClefServerError('Bad server response')


	response_object = response.json()
	token = response_object.get('access_token')

	info_url = 'https://clef.io/api/v1/info'

	params = dict(access_token=token)

	try:
		response = requests.get(info_url, params=params)
	except RequestException:
		raise ClefConnectionError('You have not established a connection')

	status_code = response.status_code

	if status_code == 403:
		# invalid token 
		raise ClefTokenError('Something went wrong on Clef"s side')

	if status_code == 500:
		raise ClefServerError('Bad server response')

	response_object = response.json()
	user_dict = response_object.get('info')
	print user_dict

	# do stuff with your user
	return user_dict 

if __name__ == '__main__':
	api = ClefAPI(app_id=CLEF_APP_ID, app_secret=CLEF_APP_SECRET)
	code = 'code_1234567890'
	user_info = api.get_user_info(code=code)
	# print user_info
	# user_info = api.get_user_info(access_token='token_1234567890')
	print user_info 


