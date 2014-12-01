import requests

class ClefError(Exception):
    """Base error."""
    pass

class ClefSetupError(Exception):
    """Invalid App Id or App secret."""
    pass

class ClefCodeError(Exception):
    """OAuth handshake failed. Clef unable to exchange code for access token."""
    pass

class ClefTokenError(Exception):
    """Clef unable to exchange token for user information."""
    pass 

class ClefServerError(Exception):
    """Clef servers are down."""
    pass 

class ClefConnectionError(Exception):
    """No network connection detected."""
    pass 

class ClefLogoutError(Exception):
    """Logout hook does not match app domain or has not been configured correctly."""
    pass 

class ClefNotFoundError(Exception):
    """Invalid API endpoint was requested."""
    pass 

# Clef 403 error strings mapped to the right class of error to raise 
message_to_error_map = {
    'Invalid App ID.': ClefSetupError,
    'Invalid App.': ClefSetupError,
    'Invalid App Secret.': ClefSetupError,
    'Invalid OAuth Code.': ClefCodeError,
    'Invalid token.' : ClefTokenError,
    'Invalid Logout Token.': ClefLogoutError,
    None: ClefError,

}

def clef_error_check(func_to_decorate):
    """Return JSON decoded response from API call. Handle errors when bad response encountered."""
    def wrapper(*args, **kwargs):
        try:
            response = func_to_decorate(*args, **kwargs)
        except requests.exceptions.RequestException:
            raise ClefConnectionError(
                'Clef encountered a network connectivity problem. Are you sure you are connected to the Internet?'
            )
        else:
            raise_right_error(response)
        return response.json() # decode json  
    return wrapper 

def raise_right_error(response):
    """Raise appropriate error when bad response received."""
    if response.status_code == 200:
        return 
    if response.status_code == 500:
        raise ClefServerError('Clef servers are down.')
    if response.status_code == 403:
        message = response.json().get('error')
        error_class = message_to_error_map[message]
        if error_class == ClefTokenError:
            message = 'Something went wrong at Clef. Unable to retrieve user information with this token.'
        raise error_class(message)
    if response.status_code == 400:
        message = response.json().get('error')
        raise ClefLogoutError(message)
    if response.status_code == 404:
        raise ClefNotFoundError('Unable to retrieve the page. Are you sure the Clef API endpoint is configured right?')
    # too restrictive? 
    raise ClefError


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
        self.logout_url = '/'.join([self.api_endpoint, 'logout'])

    @clef_error_check
    def _call(self, method, url, params):
        """Return response from Clef API call."""
        request_params = {}
        if method == 'GET':
            request_params['params'] = params 
        elif method == 'POST':
            request_params['data'] = params 
        response = requests.request(method, url, **request_params)
        return response 

    def get_user_info(self, code=None, access_token=None):
        """Return Clef user info after exchanging code for OAuth token."""
        if access_token:
            return self._get_user_info(access_token)
        # do the handshake to get token
        data = dict(code=code, app_id=self.api_key, app_secret=self.api_secret)
        token_response = self._call('POST', self.authorize_url, params=data) # json decoded
        access_token = token_response.get('access_token')
        # make request with token to get user details
        info_response = self._call('GET', self.info_url, params={'access_token': access_token})
        user_info = info_response.get('info')
        return user_info 

    def _get_user_info(self, access_token):
        """Return Clef user info. Bypass OAuth handshake."""
        # TODO: check to see if access tokens can be stored by applications or if they expire
        info_response = self._call('GET', self.info_url, params={'access_token': access_token})
        user_info = info_response.get('info')
        return user_info

    def logout_user(self, logout_token):
        """Return Clef user info after exchanging logout token."""
        data = dict(logout_token=logout_token, app_id=self.api_key, app_secret=self.api_secret)
        logout_response = self._call('POST', self.logout_url, params=data)
        clef_user_id = logout_response.get('clef_id')
        return clef_user_id
 