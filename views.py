import json
import random
import string
import httplib2
import requests

from flask import Flask, make_response, render_template, request, flash, jsonify, redirect
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from models import Base, Character, CharacterDiscussion, Tier, User
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets

# Create DB engine
engine = create_engine('sqlite:///ssbmdatabase.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Init Flask app
app = Flask(__name__)
CLIENT_ID = json.loads(open('./secrets/client_secrets.json','r').read())['web']['client_id']

@app.route('/login', methods=['GET', 'POST'])
def Login():
	print login_session
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	if request.method == 'POST':
		if 'login_username' in request.form:
			status = logUserIn(username=request.form['login_username'], 
					  			password=request.form['login_password'])
			if status != None:
				return '<h1>Success! Now logged in as {}</h1>'.format(login_session['username'])
			else:
				flash('Unsuccessful login...')
				return redirect('Login')
		user = createInternalUser(name = request.form['name'], 
							username = request.form['username'], 
							email = request.form['email'], 
							password = request.form['password'], 
							Cpassword = request.form['Cpassword'])
		return redirect('/')
	return render_template('login.html', 
							login_session=convertLoginSession(login_session), 
							state=state,
							client_id=CLIENT_ID)


@app.route('/logout')
def Logout():

	clear_login_session(login_session)

	flash('You have been logged out.')
	return redirect('/')


@app.route('/')
def Home():
	return render_template('home.html',
							login_session=convertLoginSession(login_session))


@app.route('/tiers')
def Tiers():
	tiers = session.query(Tier).all()
	SS = session.query(Character).filter_by(character_tier='SS').all()
	S = session.query(Character).filter_by(character_tier='S').all()
	A = session.query(Character).filter_by(character_tier='A').all()
	B = session.query(Character).filter_by(character_tier='B').all()
	C = session.query(Character).filter_by(character_tier='C').all()
	D = session.query(Character).filter_by(character_tier='D').all()
	E = session.query(Character).filter_by(character_tier='E').all()
	F = session.query(Character).filter_by(character_tier='F').all()
	return render_template('tiers.html', 
							tiers=tiers,
							SS=SS,
							S=S,
							A=A,
							B=B,
							C=C,
							D=D,
							E=E,
							F=F,
							login_session=convertLoginSession(login_session))


@app.route('/characters/<string:char_name>', methods=['GET','POST'])
def Characters(char_name):
	character = session.query(Character).filter_by(name=char_name).first()
	if request.method == 'POST':
		message = request.form['message']
		newMessage = CharacterDiscussion(character_id = character.id,
										 username = login_session['username'],
										 message = message)
		session.add(newMessage)
		session.commit()
	
	# Get all comments about this character organized by recency
	comments = session.query(CharacterDiscussion).filter_by(character_id=character.id).order_by(CharacterDiscussion.date.desc())
	return render_template('character.html',
							character=character,
							comments=comments,
						    login_session=convertLoginSession(login_session))


@app.route('/delete/<string:char_name>/<int:post_id>', methods=['GET', 'POST'])
def DeletePost(char_name, post_id):
	character = session.query(Character).filter_by(name = char_name).first()
	if request.method == 'POST':
		if 'confirm' in request.form:
			post = session.query(CharacterDiscussion).filter_by(id=post_id).first()
			session.delete(post)
			session.commit()
		return redirect('/characters/{}'.format(char_name))
	return render_template('confirmDelete.html',
							character = character,
							post_id = post_id)


@app.route('/edit/<string:char_name>/<int:post_id>', methods=['GET', 'POST'])
def EditPost(char_name, post_id):
	character = session.query(Character).filter_by(name=char_name).first()
	oldPost = session.query(CharacterDiscussion).filter_by(id=post_id).first()
	if request.method == 'POST':
		if 'confirm' in request.form:
			newPost = request.form['message']
			oldPost.message = newPost
			session.add(oldPost)
			session.commit()
			return redirect('/characters/{}'.format(char_name))
	return render_template('editPost.html',
							oldPost=oldPost)


@app.route('/<string:char_name>/edit', methods=['GET', 'POST'])
def EditCharacter(char_name):
	character = session.query(Character).filter_by(name=char_name).first()
	if request.method == 'POST':
		newDescription = request.form['body']
		character.description = newDescription
		session.add(character)
		session.commit()
		return redirect('/characters/{}'.format(char_name))

	return render_template('editCharacter.html',
					character=character)

@app.route('/profile')
def Profile():
	return render_template('profile.html',
							login_session=convertLoginSession(login_session))


@app.route('/about')
def About():
	return render_template('about.html',
							login_session=convertLoginSession(login_session))


@app.route('/fbconnect', methods = ['POST'])
def FacebookSignIn():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.loads('Invalid state.'),401)
		response.headers['content-type'] = 'application/json'
		return response
	data = request.data
	return '<h1>{}</h1>'.format(data)

# # # # # # # # # # # # # # # # # # # # # #
# GOOGLE+ LOGIN
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
	user_id = getIDFromEmail(login_session['email'])
	if user_id is None:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	# create a flash message that lets the user know that they are logged in
	# flash('You are now logged in as {}'.format(login_session['username']))

	return redirect('/')

# Logout route
@app.route('/gdisconnect')
def gdisconnect():

	# First we want to check to make sure that they're actually logged in
	access_token = login_session.get('access_token')
	if access_token is None:
		response = make_response(json.dumps('Current user is not connected.'),401)
		response.headers['content-type'] = 'application/json'
		return response

	# Now the way that we log out is we revoke access tokens
	# To do that we send an api call to google's revoke-token uri
	url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
	h = httplib2.Http()
	result = h.request(url,'GET')[0]

	# So let's handle the response from google to revoke the token
	if result['status'] == '200':
		# Reset user's session
		clear_login_session(login_session)

		# And send the response that acknowledges that we have successfully revoked the
		# access token
		response = make_response(json.dumps('Successfully disconnected.'),200)
		response.headers['content-type'] = 'application/json'
		return response

	else:
		# If we get any response other than a 200, then we know something went wrong
		# and that we need to handle that error.
		response = make_response(json.dumps('Error disconnecting user. Failed to revoke access token.'),400)
		response.headers['content-type'] = 'application/json'
		return response

# GOOGLE+ LOGIN END
# # # # # # # # # # # # # # # # # # # # # # # #

def getIDFromEmail(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None

def getUserID(username):
	try:
		user = session.query(User).filter_by(username=username).one()
		return user.id
	except:
		return None

def createInternalUser(name, username, email, password, Cpassword):

	# If something doesn't fit login criteria, redirect back to login page
	if name == None or username == None or password == None or Cpassword == None or password != Cpassword:
		flash('Some criteria not met')
		return None

	# If the username or email already exists then flash a warning
	existingUsername = session.query(User).filter_by(username=username).first()
	existingEmail = session.query(User).filter_by(email=email).first()
	if existingUsername != None or existingEmail != None:
		return redirect('Login')

	# If it all checks out, then create a login session
	login_session['name'] = name
	login_session['username'] = username
	login_session['email'] = email

	# Write user into database
	user = User(name = name,
				username = username,
				email = email,
				password = password)

	session.add(user)
	session.commit()

	# Return username
	return login_session['username']


def logUserIn(username, password):
	user = session.query(User).filter_by(username=username).first()
	if user.password == password and user != None:
		login_session['username'] = user.username
		login_session['email'] = user.email
		login_session['picture'] = user.picture
		login_session['user_id'] = user.id
		login_session['character'] = user.main_character
		return user.id
	else:
		return None


def createUser(login_session):
	if 'email' in login_session:
		email = login_session['email']
	else:
		email = None
	if 'provider' in login_session and login_session['provider'] == 'google':
		name = login_session['username']
		username = name
	elif 'name' in login_session:
		name = login_session['name']
		if 'username' in login_session:
			username = login_session['name']
	if 'password' in login_session:
		password = login_session['password']
	else:
		password = None

	newUser = User(name=name,
				   username=username,
				   email=email,
				   password=password)
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id

def convertLoginSession(login_session):
	if 'username' in login_session:
		session = {}
		session['username'] = login_session['username']
		session['email'] = login_session['email']
		# session['picture'] = login_session['picture']
		return session
	else:
		session = None
		return session


def clear_login_session(login_session):
	if 'username' in login_session:
		del login_session['username']
	if 'state' in login_session:
		del login_session['state']
	if 'name' in login_session:
		del login_session['name']
	if 'email' in login_session:
		del login_session['email']
	if 'picture' in login_session:
		del login_session['picture']
	if 'gplus_id' in login_session:
		del login_session['gplus_id']
	if 'character' in login_session:
		del login_session['character']
	if 'user_id' in login_session:
		del login_session['user_id']
	if 'provider' in login_session:
		del login_session['provider']
	if 'user_id' in login_session:
		del login_session['user_id']
	

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.run(host='0.0.0.0', port=5001, debug=True)
