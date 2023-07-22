from flask import Flask, render_template, send_file, request, render_template_string
import signal 
import sys
import os
sys.path.append("src")
from diffing.diff_marking import Differ
from utils import list_examples, prepare_file, get_example_file


app = Flask(__name__)


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
    return render_template('policies.html', title="Policies", 
                           navBar=navBar, policies=list_examples())

@app.route('/example')
def example():
    args = request.args
    return send_file(get_example_file(args.get("folder"), args.get("file")))

@app.route('/prepare')
def prepare():
    file = request.args.get("file")
    type = request.args.get("type")
    if type and file:
        result = prepare_file(file, type)
        return render_template_string(result)
    else:
        return render_template_string("Need type and file argument")

@app.route('/diff')
def diff():
    file_old = request.args.get("old")
    file_new = request.args.get("new")
    if file_old and file_new:
        old = "~old.html"
        new = "~new.html"
        prepare_file(file_old, save=old)
        prepare_file(file_new, save=new)
        diff = Differ(old, new, make_ids=True, use_replace=True, css_file="static/diff.css")
        os.remove(old)
        os.remove(new)
        diff.save("src/webserver/~diff.html")
        return send_file("~diff.html")
    else:
        return render_template('diff.html', title="Diff", navBar=navBar, 
                               policies=list_examples(), req=request.url)

def signal_handler(sig, frame):
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    app.run(debug=True, host='localhost', port=5008)
