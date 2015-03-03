#!/usr/bin/env python
import time
from flask import Flask, render_template, request, url_for, redirect, session, current_app
import clef

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# replace these test credentials with your own
# make sure to also replace the data-app-id attribute in your clef button - line 36 in templates/index.html
CLEF_APP_ID ='4f318ac177a9391c2e0d221203725ffd'
CLEF_APP_SECRET = '2125d80f4583c52c46f8084bcc030c9b'

clef.initialize(CLEF_APP_ID, CLEF_APP_SECRET)

@app.route('/')
def home(name=None, error=None):
    if session.get('first_name'):
        name = session['first_name']

    if session.get('error'):
        error = session['error']
        del session['error']

    return render_template('index.html', name=name, error=error)

# the data-redirect-url attribute you set in your clef button - line 36 in templates/index.html
@app.route('/oauth_callback')
def clef_oauth_callback():
    code = request.args.get('code')
    # call to get user information handles the OAuth handshake
    try:
        user_dict = clef.get_login_information(code=code)
    # customize how you want to handle errors
    except (clef.InvalidAppIDError,
            clef.InvalidAppSecretError,
            clef.InvalidOAuthCodeError,
            clef.InvalidOAuthTokenError,
            clef.ServerError,
            clef.ConnectionError) as e:
        current_app.logger.error(e)
    except clef.APIError as e:
        current_app.logger.error(e)
    # client returns a dictionary of user details
    else:
        name = user_dict.get('first_name')
        session['first_name'] = name
        session['clef_id'] = user_dict.get('id')
        session['logged_in_at'] = time.time()
    return redirect(url_for('home'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    # Clef is notifying you that a user has logged out from their phone so log them out from your site
    if request.method == 'POST':
        logout_token = request.form.get('logout_token')
        # use the clef_id to look up the user in your database and update their logged_out_at field
        # http://docs.getclef.com/v1.0/docs/database-logout
        clef_id = clef.get_logout_information(logout_token=logout_token)
    return redirect(url_for('home'))

@app.route('/oauth_error')
def oauth_error():
    session['error'] = True
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
