import json
import random
import string
import httplib2
import requests

from flask import Flask, make_response, render_template, request, flash, jsonify, redirect, url_for
from flask import session as login_session
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from flask_httpauth import HTTPBasicAuth

from models import Base, Character, CharacterDiscussion, Tier, User
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets

# Create DB engine
engine = create_engine('sqlite:///ssbmdatabase.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Auth instance
auth = HTTPBasicAuth()

# Init Flask app
app = Flask(__name__)
FB_ID = '558754497970731'
FB_SECRET = 'b657c7ebccbec31303247eac3dc598c9'
CLIENT_ID = json.loads(open('./secrets/client_secrets.json','r').read())['web']['client_id']

@app.route('/login', methods=['GET', 'POST'])
def Login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	if request.method == 'POST':
		if 'login_username' in request.form:
			status = logUserIn(username=request.form['login_username'], 
					  			password=request.form['login_password'])
			if status != None:
				flash('Success! Now logged in as {}'.format(login_session['username']))
				return redirect('/')
			else:
				flash('Unsuccessful login...')
				return redirect('/login')
		createInternalUser(name = request.form['name'], 
							username = request.form['username'], 
							email = request.form['email'],
							password = request.form['password'],
							Cpassword = request.form['Cpassword'])
		return redirect('/?login_session={}'.format(login_session))
	return render_template('login.html', 
							login_session=login_session, 
							state=state,
							client_id=CLIENT_ID)


@app.route('/logout')
def Logout():

	if 'username' in login_session:
		clear_login_session(login_session)
		flash('You have been logged out.')
	else:
		flash('You were never logged in')

	return redirect('/')


@app.route('/')
def Home():
	return render_template('home.html',
							login_session=login_session)


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
							login_session=login_session)


@app.route('/characters/<string:char_name>', methods=['GET','POST'])
def Characters(char_name):
	character = session.query(Character).filter_by(name=char_name).first()
	if request.method == 'POST':
		if 'username' not in login_session:
			return redirect(url_for('Login', login_session=login_session))
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
						    login_session=login_session)


@app.route('/delete/<string:char_name>/<int:post_id>', methods=['GET', 'POST'])
def DeletePost(char_name, post_id):
	if 'username' not in login_session:
		return redirect(url_for('Login', login_session=login_session))
	character = session.query(Character).filter_by(name = char_name).first()
	if request.method == 'POST':
		if 'confirm' in request.form:
			post = session.query(CharacterDiscussion).filter_by(id=post_id).first()
			session.delete(post)
			session.commit()
		return redirect('/characters/{}'.format(char_name))
	return render_template('confirmDelete.html',
							character = character,
							post_id = post_id,
						    login_session=login_session)


@app.route('/edit/<string:char_name>/<int:post_id>', methods=['GET', 'POST'])
def EditPost(char_name, post_id):
	if 'username' not in login_session:
		return redirect(url_for('Login',login_session=login_session))
	oldPost = session.query(CharacterDiscussion).filter_by(id=post_id).first()
	if request.method == 'POST':
		if 'confirm' in request.form:
			newPost = request.form['message']
			oldPost.message = newPost
			session.add(oldPost)
			session.commit()
			return redirect('/characters/{}'.format(char_name))
	return render_template('editPost.html',
							oldPost=oldPost,
						    login_session=login_session)


@app.route('/<string:char_name>/edit', methods=['GET', 'POST'])
def EditCharacter(char_name):
	if 'username' not in login_session:
		return redirect(url_for('Login',login_session=login_session))
	if 'permission' in login_session and login_session['permission'] != 'admin':
		flash('You do not have permission to edit this character.')
		return redirect(url_for('Character',login_session=login_session))
	character = session.query(Character).filter_by(name=char_name).first()
	if request.method == 'POST':
		newDescription = request.form['body']
		character.description = newDescription
		session.add(character)
		session.commit()
		return redirect('/characters/{}'.format(char_name))

	return render_template('editCharacter.html',
							character=character,
						    login_session=login_session)

@app.route('/profile', methods=['GET', 'POST'])
def Profile():
	print('Profile route')
	print(login_session)
	if 'username' not in login_session:
		return redirect(url_for('Login', login_session=login_session))
	if request.method == 'POST':

		# Get the current user
		user = session.query(User).filter_by(username = login_session['username']).first()

		# Update the user
		user.username = request.form['username']
		user.name = request.form['name']
		user.picture = request.form['picture']
		user.main_character = request.form['main_character']
		user.email = request.form['email']
		user.permission = request.form['permission']

		# Commit to session
		session.add(user)
		session.commit()

		# Update login_session
		login_session['username'] = user.username
		login_session['name'] = user.name
		login_session['email'] = user.email
		login_session['picture'] = user.picture
		login_session['main_character'] = user.main_character
		login_session['permission'] = user.permission

	return render_template('profile.html',
							login_session=login_session)


@app.route('/about')
def About():
	return render_template('about.html',
							login_session=login_session)

# # # # # # # # # # # # # # # # # # # # # #
# FACEBOOK LOGIN
@app.route('/fbconnect', methods = ['POST'])
def FacebookSignIn():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.loads('Invalid state.'),401)
		response.headers['content-type'] = 'application/json'
		return response

	# Extract access token
	access_token = request.data

	# Make request to FB using short-term access_token
	url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}'.format(FB_ID,FB_SECRET,access_token)
	h = httplib2.Http()
	result = h.request(url,'GET')[1]

	# Get the long term request token
	results = json.loads(result)
	token = results['access_token']

	# Make api request for user data
	url = "https://graph.facebook.com/v2.8/me?access_token={}&fields=name,id,email".format(token)
	h = httplib2.Http()
	result = h.request(url,'GET')[1]
	data = json.loads(result)

	# Facebook uses a separate api call to get the profile picture
	url = 'https://graph.facebook.com/v2.8/me/picture?access_token={}&redirect=0&height=200&width=200'.format(token)
	h = httplib2.Http()
	result = h.request(url,'GET')[1]
	pic_data = json.loads(result)

	# Place profile picture into login_session
	picture = pic_data['data']['url']

	# Do this stuff only if the user didn't already exist
	# Place variables into login_session
	if not checkEmail(data['email']):
		login_session['provider'] = 'facebook'
		login_session['name'] = data['name']
		login_session['email'] = data['email']
		login_session['user_id'] = data['id']
		login_session['picture'] = picture

		# Create a temporary username
		username = createUsername(login_session['name'])

		# Place username into login_session
		login_session['username'] = username

		# Place into database
		createUser(login_session)

	else:
		user = session.query(User).filter_by(email=data['email']).first()
		login_session['provider'] = 'facebook'
		login_session['name'] = user.name
		login_session['username'] = user.username
		login_session['email'] = user.email
		login_session['picture'] = user.picture
		login_session['main_character'] = user.main_character
		login_session['permission'] = user.permission


	# Display success and return home
	flash('Success! Now logged in as {}.'.format(login_session['username']))
	return render_template('home.html',
							login_session=login_session)

# END FACEBOOK LOGIN
# # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # #
# GOOGLE+ LOGIN
@app.route('/gconnect', methods = ['POST'])
def gconnect():
	
	state = request.args.get('state')
	print(state)
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
	
	# If this user's email already exists, stop here and just log that user in
	if checkEmail(data['email']):
		user = session.query(User).filter_by(email = data['email']).first()
		login_session['name'] = user.name
		login_session['username'] = user.username
		login_session['email'] = user.email
		login_session['main_character'] = user.main_character
		login_session['picture'] = user.picture
		login_session['provider'] = 'google'
		login_session['permission'] = user.permission
		
		flash('Success! Now logged in as {}.'.format(login_session['username']))
		return render_template('home.html',
								login_session=login_session)

	# Store user info in our login_session
	login_session['provider'] = 'google'
	login_session['name'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	# Create a username for them since google doesn't give us that
	username = createUsername(login_session['name'])
	login_session['username'] = username

	# If we don't have the user's email, create the user
	createUser(login_session)
	
	# create a flash message that lets the user know that they are logged in
	flash('Success! Now logged in as {}'.format(login_session['username']))
	return render_template('home.html',
							login_session=login_session)

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
		print('Some criteria not met')
		return None
	
	# Check if the username exists, if it does then generate one
	existingUsername = session.query(User).filter_by(username=username).first()
	if existingUsername is not None:
		username = createUsername(name)

	# Check if the email exists, if it does, tell them to just log in
	existingEmail = session.query(User).filter_by(email=email).first()
	if existingEmail is not None:
		flash('That email already exists, just log in!')
		return redirect(url_for('Login',login_session=login_session))

	
	# If it all checks out, then create a login session
	login_session['name'] = name
	login_session['username'] = username
	login_session['email'] = email
	login_session['permission'] = 'standard'
	
	# Write user into database
	user = User(name = name,
				username = username,
				email = email,
				permission = login_session['permission'])
	user.hash_password(password)
	session.add(user)
	session.commit()
	
	# Return username
	return login_session['username']


def logUserIn(username, password):
	user = session.query(User).filter_by(username=username).first()
	if user != None and user.verify_password(password):
		login_session['name'] = user.name
		login_session['username'] = user.username
		login_session['email'] = user.email
		login_session['picture'] = user.picture
		login_session['user_id'] = user.id
		login_session['main_character'] = user.main_character
		login_session['permission'] = user.permission
		return user.id
	else:
		return None


def createUser(login_session):
	if 'email' in login_session:
		email = login_session['email']
	elif 'email' in login_session and checkEmail(login_session['email']):
		flash('That email address already exists.')
		return render_template('login.html',
								login_session=login_session)
	if 'username' in login_session:
		username = login_session['username']
	if 'name' in login_session:
		name = login_session['name']
	login_session['permission'] = 'standard'
	newUser = User(name=name,
				   username=username,
				   email=email,
				   permission=login_session['permission'])
	if 'password' in login_session:
		newUser.hash_password(login_session['password'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).first()
	return user.id


def checkEmail(email):
	user = session.query(User).filter_by(email = email).first()
	if user is None:
		return False
	else:
		return True


def checkUsername(username):
	user = session.query(User).filter_by(username = username).first()
	if user is None:
		return False
	else:
		return True


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
	if 'main_character' in login_session:
		del login_session['main_character']
	if 'user_id' in login_session:
		del login_session['user_id']
	if 'provider' in login_session:
		del login_session['provider']
	if 'user_id' in login_session:
		del login_session['user_id']
	if 'access_token' in login_session:
		del login_session['access_token']
	if 'permission' in login_session:
		del login_session['permission']


def createUsername(name):
	name = name.replace(' ', '-')
	iterator = 0
	username = name + '-' + str(iterator)
	user = session.query(User).filter_by(username = username).first()
	while(user is not None):
		iterator += 1
		username = name + '-' + str(iterator)
		user = session.query(User).filter_by(username = username).first()
	return username

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.run(host='0.0.0.0', port=5001, debug=True)
