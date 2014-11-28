#!/usr/bin/env python

import json
import unittest

import mock
import httpretty
import requests

from clef import clef

TEST_APP_ID = '4f318ac177a9391c2e0d221203725ffd'
TEST_APP_SECRET = '2125d80f4583c52c46f8084bcc030c9b'
TEST_CODE = 'code_1234567890'
TEST_TOKEN = 'token_1234567890'

class ClefConfigTests(unittest.TestCase):
    """Make sure basic init is set up correctly."""
    def test_default_configuration(self):
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET)
        self.assertEqual(self.api.api_key, TEST_APP_ID)
        self.assertEqual(self.api.api_secret, TEST_APP_SECRET)
        self.assertEqual(self.api.api_endpoint, 'https://clef.io/api/v1')
        self.assertEqual(self.api.authorize_url, 'https://clef.io/api/v1/authorize')
        self.assertEqual(self.api.info_url, 'https://clef.io/api/v1/info')
        self.assertEqual(self.api.logout_url, 'https://clef.io/api/v1/logout')

    def test_changing_root_config(self):
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET, root='https://getclef.com')
        self.assertEqual(self.api.api_endpoint, 'https://getclef.com/v1')
        self.assertEqual(self.api.authorize_url, 'https://getclef.com/v1/authorize')
        self.assertEqual(self.api.info_url, 'https://getclef.com/v1/info')
        self.assertEqual(self.api.logout_url, 'https://getclef.com/v1/logout')

class ClefIntegrationTests(unittest.TestCase):
    """Verify that endpoints are working with test credentials."""
    def setUp(self):
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET)

    def test_endpoints(self):
        response = requests.get(self.api.authorize_url)
        self.assertFalse(str(response.status_code).startswith('5'))
        response = requests.get(self.api.info_url)
        self.assertFalse(str(response.status_code).startswith('5'))
        logout_url = '/'.join([self.api.api_endpoint, 'logout'])
        response = requests.get(logout_url)
        self.assertFalse(str(response.status_code).startswith('5'))

    def test_get_user_info(self):
        """Return user info when a valid code is passed in."""
        user_info = self.api.get_user_info(code=TEST_CODE)
        self.assertTrue(isinstance(user_info, dict))
        self.assertEqual(user_info['id'], '12345')

    def test_get_user_info_without_handshake(self):
        """ Bypass OAuth handshake when access_token passed in """
        user_info = self.api.get_user_info(access_token=TEST_TOKEN)
        self.assertTrue(isinstance(user_info, dict))
        self.assertEqual(user_info['id'], '12345')

class ClefMockCallTests(unittest.TestCase):
    def setUp(self):
        self.api = clef.ClefAPI(app_id='fake_id', app_secret='fake_secret')

    def test_get_user_info(self):
        """Verify get_user_info makes the right calls."""
        code = 'fake_code'
        self.api._call = mock.Mock()
        self.api.get_user_info(code=code)

        # verify. mock calls are tuples of positional and keyword arguments
        self.assertEqual(self.api._call.call_count, 2)
        call_args = self.api._call.call_args_list
        authorize_call = call_args[0]
        authorize_pos_args = authorize_call[0]
        authorize_kwargs = authorize_call[1]
        self.assertEqual(authorize_pos_args, ('POST', self.api.authorize_url))
        self.assertTrue('params' in authorize_kwargs)
        self.assertTrue(isinstance(authorize_kwargs['params'], dict))

        info_call = call_args[1]
        info_pos_args = info_call[0]
        info_kwargs = info_call[1]
        token = self.api._call().get()
        self.assertEqual(info_pos_args, ('GET', self.api.info_url))
        self.assertEqual(info_kwargs, ({'params': {'access_token': token}}))

    def test_logout_user(self):
        """Verify logout_user makes the right calls."""
        logout_token = 'fake_token'
        self.api._call = mock.Mock()
        self.api.logout_user(logout_token=logout_token)

        # verify right calls are made
        self.assertEqual(self.api._call.call_count, 1)
        call_args = self.api._call.call_args_list
        exchange_call = call_args[0]
        exchange_pos_args = exchange_call[0]
        exchange_kwargs = exchange_call[1]
        self.assertEqual(exchange_pos_args, ('POST', self.api.logout_url))
        self.assertTrue('params' in exchange_kwargs)
        self.assertTrue(isinstance(exchange_kwargs['params'], dict))

class ClefAPITests(unittest.TestCase):
    """Verify the appropriate error is raised according to the endpoint and reponse status code."""
    def setUp(self):
        self.api = clef.ClefAPI(app_id='fake_id', app_secret='fake_secret')
        self.code = 'fake_code'
        self.token = 'fake_token'
        self.good_info_response = {'success': True}
        user_details = dict(first_name='Alex', id='12345', email='alex@getclef.com')
        self.good_info_response['info'] = user_details
    
    @httpretty.activate
    def test_invalid_app_id_error(self):
        httpretty.register_uri(httpretty.POST, "https://clef.io/api/v1/authorize",
                           body='{"error": "Invalid App ID."}',
                           content_type="text/json",
                           status=403)
        self.assertRaises(clef.ClefSetupError, self.api.get_user_info, code=self.code)

    @httpretty.activate
    def test_invalid_app_secret_error(self):
        httpretty.register_uri(httpretty.POST, self.api.authorize_url,
                                body='{"error": "Invalid App Secret."}',
                                content_type="text/json",
                                status=403)
        self.assertRaises(clef.ClefSetupError, self.api.get_user_info, code=self.code)

    @httpretty.activate
    def test_invalid_oauth_code(self):
        httpretty.register_uri(httpretty.POST, self.api.authorize_url,
                                body='{"error": "Invalid OAuth Code."}',
                                content_type="text/json",
                                status=403)
        self.assertRaises(clef.ClefCodeError, self.api.get_user_info, code=self.code)

    @httpretty.activate
    def test_valid_credentials_and_code(self):
        """Verify no error is raised when API calls return status code 200."""
        httpretty.register_uri(httpretty.POST, "https://clef.io/api/v1/authorize",
                                body='{"success": "true", "access_token": "fake_token"}',
                                content_type="text/json",
                                status=200)
    
        httpretty.register_uri(httpretty.GET, "https://clef.io/api/v1/info",
                           body=json.dumps(self.good_info_response),
                           content_type="text/json",
                           status=200)

        user_info = self.api.get_user_info(code=self.code)
        self.assertEqual(user_info['first_name'], 'Alex')
        self.assertEqual(user_info['id'], '12345')
        self.assertEqual(user_info['email'], 'alex@getclef.com')

    @httpretty.activate
    def test_invalid_token(self):
        httpretty.register_uri(httpretty.GET, self.api.info_url,
                           body=json.dumps(dict(error='Invalid token.')),
                           content_type="text/json",
                           status=403)
        self.assertRaises(clef.ClefTokenError, self.api._call, 'GET', self.api.info_url, {'access_token': self.token})

    @httpretty.activate
    def test_valid_token(self):
        httpretty.register_uri(httpretty.GET, self.api.info_url,
                           body=json.dumps(self.good_info_response),
                           content_type="text/json",
                           status=200)
        response = self.api._call('GET', self.api.info_url, {'access_token': self.token})
        user_info = response['info']
        self.assertEqual(user_info['first_name'], 'Alex')
        self.assertEqual(user_info['id'], '12345')
        self.assertEqual(user_info['email'], 'alex@getclef.com')


    @httpretty.activate
    def test_invalid_logout_hook(self):
        httpretty.register_uri(httpretty.POST, self.api.authorize_url,
                                body='{"error": "Invalid logout hook URL."}',
                                content_type="text/json",
                                status=400)
        data = dict(app_id=self.api.api_key, app_secret=self.api.api_secret, code=self.code)
        self.assertRaises(clef.ClefLogoutError, self.api._call, 'POST', self.api.authorize_url, data)

if __name__ == '__main__':
    unittest.main()
