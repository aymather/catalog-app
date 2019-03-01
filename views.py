import json
import random
import string
import httplib2
import requests

from flask import Flask, make_response, render_template, request, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Character, CharacterDiscussion, Tier, User
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets

# Create DB engine
engine = create_engine('sqlite:///ssbmdatabase.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Init Flask app
app = Flask(__name__)
CLIENT_ID = json.loads(open('./secrets/client_secrets.json','r').read())['web']['client_id']

@app.route('/login')
def Login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return render_template('login.html', state=login_session['state'], client_id=CLIENT_ID)


@app.route('/')
def Home():
	return render_template('home.html')


@app.route('/tiers')
def Tiers():
	tiers = session.query(Tier).all()
	return render_template('tiers.html', tiers = tiers)


@app.route('/profile')
def Profile():
	return render_template('profile.html')


@app.route('/about')
def About():
	return render_template('about.html')


@app.route('/fbconnect', methods = ['POST'])
def FacebookSignIn():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.loads('Invalid state.'),401)
		response.headers['content-type'] = 'application/json'
		return response
	data = request.data
	return '<h1>It worked!</h1>'


@app.route('/gconnect', methods = ['POST'])
def gconnect():
	state = request.args.get('state')
	if state != login_session['state']:
		response = make_response(json.dumps('Invalid state. Redirecting...'),401)
		response.headers['Content-Type'] = 'application/json'
		return response
	oneTimeCode = request.data
	if oneTimeCode is None:
		response = make_response(json.dumps('Missing one time code. Try again.'),401)
		response.headers['content-type'] = 'application/json'
		return response
	# Try exchanging one time code for access_token
	try:
		oauth = flow_from_clientsecrets('./secrets/client_secrets.json',scope='')
		oauth.redirect_uri = 'postmessage'
		credentials = oauth.step2_exchange(oneTimeCode)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to make oauth flow exchange.'),500)
		response.headers['content-type'] = 'application/json'
		return response
	
	# Get user info with access_token
	access_token = credentials.access_token
	url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	
	# Check for error from request
	if result.get('error') is not None:
		# dump the error to the client in json format
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['content-type'] = 'application/json'
		return response

	# Verify user's token id 
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."),401)
		response.headers['content-type'] = 'application/json'
		return response

	# Verify that the access token is for THIS app
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's client id"), 401)
		response.headers['content-type'] = 'application/json'
		return response

	# Check to see if the user is already logged into the system
	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),200)
		response.headers['content-type'] = 'applcation/json'
		return response

	# Now store the access token in the session for later use
	login_session['access_token'] = access_token
	login_session['gplus_id'] = gplus_id

	# Now use the googleplus api to get more info about the user
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt':'json'}
	answer = requests.get(userinfo_url,params=params)
	data = answer.json()

	# Store user info in our login_session
	login_session['provider'] = 'google'
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	# If we don't have the user's email, create the user
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	# create a flash message that lets the user know that they are logged in
	flash('You are now logged in as {}'.format(login_session['username']))

	# Create an output that displays the username and stuff
	output = '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += '" style="width:300px;height:300px;border-radius:150px;-webkit-border-radius:150px;-moz-border-radius:150px;">'
	return output


def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None

def createUser(login_session):
	newUser = User(name=login_session['username'],
				   email=login_session['email'],
				   picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id
	

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.run(host='0.0.0.0', port=5001, debug=True)
