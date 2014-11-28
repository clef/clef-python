clef-python
=================================
A Python wrapper for the [Clef](https://getclef.com/) API.      
Authenticate a user and access their information with four lines of code. 


Requires
--------
* requests

Getting Started
-----------
The Clef API uses OAuth2 for authentication. Pass your credentials to the ClefAPI constructor and make
a single call to handle the handshake and retrieve user information.

# Get your credentials
[Create a Clef application](http://docs.getclef.com/v1.0/docs/creating-a-clef-application) to get your App ID and App secret

# Add the Clef button
The [button](http://docs.getclef.com/v1.0/docs/adding-the-clef-button) has a `data-redirect-url` which is where you will handle the OAuth callback. It can be customized or generated.

Usage
-----

# Handle OAuth callback
When a user logs in with Clef, Clef will send a code to the redirect url you defined in the button, which is where you handle the callback:
``` 
from clef import clef

code = request.args.get("code")
api = ClefAPI(app_id="YOUR_APP_ID", app_secret="YOUR_APP_SECRET")
user_info = api.get_user_info(code=code)
```
# Handle logout callback
When you configure your application, you also set up a logout hook so Clef can notify you when a user logs out of their phone.
```
from clef import Clef

logout_token = request.form.get("logout_token")
api = ClefAPI(app_id="YOUR_APP_ID", app_secret="YOUR_APP_SECRET")
clef_user_id = api.logout_user(logout_token=logout_token)
```

Sample App
----------
This repo includes a one-file sample app that uses the Flask framework and demonstrates authentication. To try it out:
* Install Flask `pip install flask`
* Run sample_app.py `python sample_app.py`
* Visit http://localhost:5000 in your browser

The sample app doesn't handle [checking timestamped logins](http://docs.getclef.com/v1.0/docs/checking-timestamped-logins), but there are [code samples](http://docs.getclef.com/v1.0/docs/overview-1) that demonstrate how to do this.

 
Resources
--------
Check out the [API docs](http://docs.getclef.com/v1.0/docs/).   
Access your [developer dashboard](https://getclef.com/user/login)