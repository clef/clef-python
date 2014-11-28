import time 
from flask import Flask, render_template, request, url_for, redirect, session
from clef import clef 

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# replace these test credentials with your own 
CLEF_APP_ID ='4f318ac177a9391c2e0d221203725ffd'  
CLEF_APP_SECRET = '2125d80f4583c52c46f8084bcc030c9b'


@app.route('/')
def home(name=None, error=None):
    if session.get('first_name'):
        name = session['first_name']

    if session.get('error'):
        error = session['error']
        del session['error']
    
    return render_template('index.html', name=name, error=error)

# the data-redirect-url attribute you set in your clef button
# line 31 in templates/index.html
@app.route('/oauth_callback')
def clef_oauth_callback():
    # configure the client 
    code = request.args.get('code')
    client = clef.ClefAPI(app_id=CLEF_APP_ID, app_secret=CLEF_APP_SECRET)
    # call to get user information handles the OAuth handshake
    try:
        user_dict = client.get_user_info(code=code)
    # customize how you want to handle errors
    except (clef.ClefSetupError, 
            clef.ClefTokenError, 
            clef.ClefCodeError, 
            clef.ClefServerError, 
            clef.ClefConnectionError) as e:
            pass
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
    if request.method == 'POST':
        # Clef is notifying you that a user has logged out from their phone so log them out from your site 
        logout_token = request.form.get('logout_token')
        client = clef.ClefAPI(app_id=CLEF_APP_ID, app_secret=CLEF_APP_SECRET)
        clef_user_id = client.logout_user(logout_token=logout_token) 
        # use the clef_user_id to look up the user in your database and update their logged_out_at field
        # http://docs.getclef.com/v1.0/docs/database-logout
    return redirect(url_for('home'))

@app.route('/oauth_error')
def oauth_error():
    session['error'] = True
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)