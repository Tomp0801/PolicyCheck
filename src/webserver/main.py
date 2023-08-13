from flask import Flask, render_template, send_file, request, render_template_string
import signal 
import sys
import os
sys.path.append("src")
from diffing.diff_marking import Differ
from utils import list_examples, prepare_file, get_example_file


app = Flask(__name__)

style_options = {
    "Strikethrough" : "diff_strikethrough.css",
    "Tooltips" : "diff_tooltips.css"
}
css_style = "Strikethrough"

navBar = [
	{'name':'Home', 'href':'/'},
	{'name':'Policies', 'href':'/policies'},
    {'name':'Diff', 'href':'/diff'}
]

def render_with_layout(template, title, **kwargs):
    return render_template(template, title=title, navBar=navBar, 
                           css_file=style_options[css_style], **kwargs)


@app.route('/')
def home():
    return render_with_layout('index.html', title="Home", page_content="Hello there")

@app.route('/policies')
def policies():
    return render_with_layout('policies.html', title="Policies", 
                           policies=list_examples())

@app.route('/example')
def example():
    args = request.args
    return render_with_layout("file.html", title="Policies",
                              html_file=get_example_file(args.get("folder"), args.get("file")))

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
        diff = Differ(old, new, make_ids=True, use_replace=True)
        os.remove(old)
        os.remove(new)
        diff.save("src/webserver/templates/~diff.html", add_head=False)
        return render_with_layout("file.html", title="Diff", 
                               html_file="~diff.html")
    else:
        return render_with_layout('diff.html', title="Diff", 
                               policies=list_examples(), req=request.url)

@app.route('/style')
def set_style():
    global css_style
    style = request.args.get("style")
    if style in style_options.keys():
        css_style = style
    return render_with_layout('index.html', title="Home", page_content="Hello there")

def signal_handler(sig, frame):
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    app.run(debug=True, host='localhost', port=5008)
