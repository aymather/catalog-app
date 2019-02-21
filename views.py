from flask import Flask, render_template, request, make_response
from flask import session as login_session
import random, string, json
from oauth2client.client import flow_from_clientsecrets # used to exchange one time codes for access_token
from oauth2client.client import FlowExchangeError # handles exceptions in flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Character, CharacterDiscussion, Tier

# Create DB engine
engine = create_engine('sqlite:///ssbmdatabase.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Init Flask app
app = Flask(__name__)


@app.route('/login')
def Login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return render_template('login.html', state=login_session['state'])


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
def GoogleSignIn():
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
		oauth_flow = flow_from_clientsecrets('./secrets/google_client_secrets.json',scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(oneTimeCode)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to make oauth flow exchange.'),500)
		response.headers['content-type'] = 'application/json'
		return response
	
	return render_template('home.html')
	

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.run(host='0.0.0.0', port=5001,debug=True)