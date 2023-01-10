from flask import Flask, jsonify, request, g, render_template, send_from_directory
from flask_cors import CORS
import json
import os


app = Flask(__name__, static_folder='static/')
cors = CORS(app, resources={r"/*": {"origins": "*"}})

settings = {}

if os.path.exists("setting.json"):
    fp = open("setting.json", 'r', encoding="utf-8")
    settings = json.load(fp)
    fp.close()


def replace_variable(in_file, out_file):
    fp_in = open(in_file, 'r', encoding="utf-8")
    text = fp_in.read()
    fp_in.close()
    text = text.replace("${IDSERVER_ENDPOINT}", settings["idserver_endpoint"])
    text = text.replace("${REPOAPI_ENDPOINT}", settings["repoapi_endpoint"])

    fp_out = open(out_file, 'w', encoding="utf-8")
    fp_out.write(text)
    fp_out.close()


replace_variable("static/enonce.md", "static/enonce_dist.md")
replace_variable("static/tasks.md", "static/tasks_dist.md")


@app.route("/")
def home():
    return render_template('index.html', **settings)


@app.route("/snippetsspec.html")
def snippet_spec():
    return render_template('snippetsspec.html', **settings)


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


if __name__ == '__main__':
    app.run()
