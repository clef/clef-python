python-clef
=================================

A Python wrapper for the [Clef](https://getclef.com/) API. Authenticate a user and access their information in two lines of code. 


Installation
------------

Install using pip:        

 ```
 pip install clef
 ```

Getting Started
-----------

The Clef API lets you retrieve information about a user after they log in to your site with Clef. 

#### Get your API credentials

[Create a Clef application](http://docs.getclef.com/v1.0/docs/creating-a-clef-application) to get your App ID and App secret.

#### Add the Clef button

The [Clef button](http://docs.getclef.com/v1.0/docs/adding-the-clef-button) has a `data-redirect-url`, which is where you can retrieve user information.

Usage
-----

#### Logging in a user

When a user logs in with Clef, the browser will redirect to your `data-redirect-url`. To retrieve user information, call `get_login_information` in that endpoint: 

``` 
import clef

clef.initialize(app_id=YOUR_APP_ID, app_secret=YOUR_APP_SECRET)

# In your redirect URL route: 
code = request.args.get('code')
user_information = clef.get_login_information(code=code)
```

For what to do after getting user information, check out our documentation on
[Associating users](http://docs.getclef.com/v1.0/docs/persisting-users).

#### Logging out a user

When you configure your Clef integration, you can also set up a logout hook URL. Clef sends a POST to this URL whenever a user logs out with Clef, so you can log them out on your website too.

```
import clef

clef.initialize(app_id=YOUR_APP_ID, app_secret=YOUR_APP_SECRET)

# In your logout hook route:
logout_token = request.form.get("logout_token")
clef_id = clef.get_logout_information(logout_token=logout_token)
```

For what to do after getting a user who's logging out's `clef_id`, see our
documentation on [Database
logout](http://docs.getclef.com/v1.0/docs/database-logout).


Sample App
----------

This repo includes a one-file sample app that uses the Flask framework and demonstrates authentication. To try it out:    
* Install Flask if you don't already have it      
`$ pip install Flask`    
* Run sample_app.py     
`$ python sample_app.py`          
* Visit http://localhost:5000 in your browser      

The sample app doesn't handle [checking timestamped logins](http://docs.getclef.com/v1.0/docs/checking-timestamped-logins), but there are [code samples](http://docs.getclef.com/v1.0/docs/overview-1) that demonstrate how to do this.

 
Resources
--------
Check out the [API docs](http://docs.getclef.com/v1.0/docs/).     
Access your [developer dashboard](https://getclef.com/user/login).
