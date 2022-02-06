from flask import Flask, render_template
import signal 
import sys

from versioning import Versioning

app = Flask(__name__)

navBar = [
	{'name':'Home', 'href':'/'},
	{'name':'Policies', 'href':'/policies'}
]

policyLinks = [
    "https://www.redditinc.com/policies/user-agreement"
]

@app.route('/')
def home():
    return render_template('index.html', title="Home", navBar=navBar)

@app.route('/policies')
def policies():
    return render_template('policies.html', title="Policies", navBar=navBar)

def signal_handler(sig, frame):
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    ver = Versioning("policies")

    #app.run(debug=True, host='localhost', port=5008)