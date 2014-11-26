import unittest
from clef import clef

TEST_APP_ID = '4f318ac177a9391c2e0d221203725ffd'
TEST_APP_SECRET = '2125d80f4583c52c46f8084bcc030c9b'
TEST_CODE = 'code_1234567890'
TEST_TOKEN = 'token_1234567890'

class ClefConfigTests(unittest.TestCase):
    
    def test_configuration(self):
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET)
        self.assertEqual(self.api.api_key, TEST_APP_ID)
        self.assertEqual(self.api.api_secret, TEST_APP_SECRET)
        self.assertEqual(self.api.api_endpoint, 'https://clef.io/api/v1')
        self.assertEqual(self.api.authorize_url, 'https://clef.io/api/v1/authorize')
        self.assertEqual(self.api.info_url, 'https://clef.io/api/v1/info')

    def test_optional_root(self):
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET, root='https://getclef.com')
        self.assertEqual(self.api.api_endpoint, 'https://getclef.com/v1')
        self.assertEqual(self.api.authorize_url, 'https://getclef.com/v1/authorize')
        self.assertEqual(self.api.info_url, 'https://getclef.com/v1/info')

class ClefOAuthTests(unittest.TestCase):
    def setUp(self):
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET)
        self.data = dict(code=TEST_CODE, app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET)

    def test_exchange_code_for_oauth_token(self):
        response_object = self.api._call('POST', self.api.authorize_url, params=self.data)
        self.assertTrue(response_object.get('success'))
        self.assertEqual(response_object.get('access_token'), TEST_TOKEN)

    def test_exchange_bad_code_for_oauth_token(self):
        invalid_code = 'invalid_code'
        self.data['code'] = invalid_code
        self.assertRaises(clef.ClefCodeError, self.api._call, 'POST', self.api.authorize_url, self.data)

    def test_exchange_null_code_for_oauth_token(self):
        invalid_code = ''
        self.data['code'] = invalid_code
        self.assertRaises(clef.ClefCodeError, self.api._call, 'POST', self.api.authorize_url, self.data)

class ClefTokenTests(unittest.TestCase):
    def setUp(self):
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET)
        self.data = dict(access_token=TEST_TOKEN)

    def test_get_user_info_with_token(self):
        response_object = self.api._call('GET', self.api.info_url, params=self.data)
        self.assertTrue(response_object.get('success'))
        user_info = response_object.get('info')
        self.assertTrue(isinstance(user_info, dict))

    def test_get_user_info_with_bad_token(self):
        invalid_token = 'invalid_token'
        self.data['access_token'] = invalid_token
        self.assertRaises(clef.ClefTokenError, self.api._call, 'GET', self.api.info_url, self.data)

class ClefAPITests(unittest.TestCase):
    def setUp(self):
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=TEST_APP_SECRET)

    def test_get_user_info(self):
        """ Client only has to pass in code to get the details they want """
        user_info = self.api.get_user_info(code=TEST_CODE)
        self.assertTrue(isinstance(user_info, dict))
        self.assertEqual(user_info.get('id'), '12345')

    def test_get_user_info_without_handshake(self):
        """ If client passes in optional token parameter, oauth handshake should be bypassed """
        user_info = self.api.get_user_info(access_token=TEST_TOKEN)
        self.assertTrue(isinstance(user_info, dict))
        self.assertEqual(user_info.get('id'), '12345')

    def test_get_user_info_with_invalid_code(self):
        invalid_code = 'invalid_code'
        self.assertRaises(clef.ClefCodeError, self.api.get_user_info, code=invalid_code)

    def test_get_user_info_with_invalid_token(self):
        invalid_token = 'invalid_token'
        self.assertRaises(clef.ClefTokenError, self.api.get_user_info, access_token=invalid_token)

    def test_get_user_info_with_invalid_app_id(self):
        # TODO: temporary hack to test set up error, if you pass in valid code, the setup error does not get raised
        self.api = clef.ClefAPI(app_id=None, app_secret=TEST_APP_SECRET)
        self.assertRaises(clef.ClefSetupError, self.api.get_user_info, code='')

    def test_get_user_info_with_invalid_app_secret(self):
        # TODO: temporary hack to test set up error, if you pass in valid code, the setup error does not get raised
        self.api = clef.ClefAPI(app_id=TEST_APP_ID, app_secret=None)
        self.assertRaises(clef.ClefSetupError, self.api.get_user_info, code='')


        






if __name__ == '__main__':
    unittest.main()

    





