from flask import Flask, render_template
from flask import session as login_session
import random, string

app = Flask(__name__)


@app.route('/login')
def Login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return render_template('login.html', session=login_session)


@app.route('/')
def Home():
	return render_template('home.html')
	

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.run(host='0.0.0.0', port=5001,debug=True)