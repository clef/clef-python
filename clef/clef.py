import requests

class APIError(Exception): pass
class InvalidAppIDError(APIError): pass
class InvalidAppSecretError(APIError): pass
class InvalidAppError(APIError): pass
class InvalidOAuthCodeError(APIError): pass
class InvalidOAuthTokenError(APIError): pass
class InvalidLogoutHookURLError(APIError): pass
class InvalidLogoutTokenError(APIError): pass
class ServerError(APIError): pass
class ConnectionError(APIError): pass
class NotFoundError(APIError): pass



# Clef 403 error strings mapped to the right class of error to raise
MESSAGE_TO_ERROR_MAP = {
    'Invalid App ID.': InvalidAppIDError,
    'Invalid App Secret.': InvalidAppSecretError,
    'Invalid App.': InvalidAppError,
    'Invalid OAuth Code.': InvalidOAuthCodeError,
    'Invalid token.': InvalidOAuthTokenError,
    'Invalid logout hook URL.': InvalidLogoutHookURLError,
    'Invalid Logout Token.': InvalidLogoutTokenError,
    None: APIError
}

def clef_error_check(func_to_decorate):
    """Return JSON decoded response from API call. Handle errors when bad response encountered."""
    def wrapper(*args, **kwargs):
        try:
            response = func_to_decorate(*args, **kwargs)
        except requests.exceptions.RequestException:
            raise ConnectionError(
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
        raise ServerError('Clef servers are down.')
    if response.status_code == 403:
        message = response.json().get('error')
        error_class = MESSAGE_TO_ERROR_MAP[message]
        if error_class == InvalidOAuthTokenError:
            message = 'Something went wrong at Clef. Unable to retrieve user information with this token.'
        raise error_class(message)
    if response.status_code == 400:
        message = response.json().get('error')
        error_class = MESSAGE_TO_ERROR_MAP[message]
        if error_class:
            raise error_class(message)
        else:
            raise InvalidLogoutTokenError(message)
    if response.status_code == 404:
        raise NotFoundError('Unable to retrieve the page. Are you sure the Clef API endpoint is configured right?')
    raise APIError


class ClefAPI(object):
    def __init__(self, app_id=None, app_secret=None, root=None):
        if not root:
            root = 'https://clef.io/api'
        version = 'v1'
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_endpoint = '{0}/{1}'.format(root, version)
        self.authorize_url = '{0}/authorize'.format(self.api_endpoint)
        self.info_url = '{0}/info'.format(self.api_endpoint)
        self.logout_url = '{0}/logout'.format(self.api_endpoint)

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

    def get_login_information(self, code=None):
        """Return Clef user info after exchanging code for OAuth token."""
        # do the handshake to get token
        access_token = self._get_access_token(code)
        # make request with token to get user details
        return self._get_user_info(access_token)

    def _get_access_token(self, code):
        data = dict(
            code=code,
            app_id=self.app_id,
            app_secret=self.app_secret
        )
        # json decoded
        token_response = self._call('POST', self.authorize_url, params=data)
        return token_response.get('access_token')

    def _get_user_info(self, access_token):
        """Return Clef user info."""
        info_response = self._call('GET', self.info_url, params={'access_token': access_token})
        user_info = info_response.get('info')
        return user_info

    def get_logout_information(self, logout_token):
        """Return Clef user info after exchanging logout token."""
        data = dict(logout_token=logout_token, app_id=self.app_id, app_secret=self.app_secret)
        logout_response = self._call('POST', self.logout_url, params=data)
        clef_user_id = logout_response.get('clef_id')
        return clef_user_id


clef_api = ClefAPI()

def initialize(app_id=None, app_secret=None):
    global clef_api
    if not clef_api:
        clef_api = ClefAPI()
    clef_api.app_id = app_id
    clef_api.app_secret = app_secret

def get_login_information(code):
    global clef_api
    return clef_api.get_login_information(code=code)

def get_logout_information(logout_token):
    global clef_api
    return clef_api.get_logout_information(logout_token)

