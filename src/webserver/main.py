from flask import Flask, render_template, send_file, request, render_template_string
import signal 
import sys
import os 
sys.path.append("src/scraping")
from adapters import RedditAdapter, GoogleAdapter


app = Flask(__name__)

examples_path = "examples/html"

navBar = [
	{'name':'Home', 'href':'/'},
	{'name':'Policies', 'href':'/policies'},
    {'name':'Diff', 'href':'/diff'}
]

policyLinks = [
    "https://www.redditinc.com/policies/user-agreement"
]

@app.route('/')
def home():
    return render_template('index.html', title="Home", navBar=navBar)

@app.route('/policies')
def policies():
    policies = {}
    folders = os.listdir(examples_path)
    for folder in folders:
        policies[folder] = os.listdir(os.path.join(examples_path, folder))
    return render_template('policies.html', title="Policies", navBar=navBar, policies=policies)

@app.route('/example')
def example():
    args = request.args
    return send_file(os.path.join(examples_path, args.get("folder"), args.get("file")))

@app.route('/prepare')
def prepare():
    file = request.args.get("file")
    type = request.args.get("type")
    if type and file:
        file = os.path.join(examples_path, file)
        save_file = "tmp.html"
        if type=="reddit":
            adap = RedditAdapter(file)
        elif type=="google":
            adap = GoogleAdapter(file)
        adap.save(save_file)
        return render_template_string(adap._soup.prettify())

@app.route('/diff')
def diff():

    return render_template('diff.html', title="Diff", navBar=navBar)

def signal_handler(sig, frame):
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    app.run(debug=True, host='localhost', port=5008)