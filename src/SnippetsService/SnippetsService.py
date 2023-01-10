from flask import Flask, request, g, jsonify
from flask_cors import CORS
import json
from Store.MySQL.SnippetsStore import SnippetsStore
from Services.SnippetsService import SnippetsService
from OpenIdClient import OpenIdClient, RequiredClaimsPolicy, ClaimValueValidator
from RestAPI import *

def loadSettings(filepath):
    fp = open(filepath, 'r')
    settings = json.load(fp)
    fp.close()

    return settings

app = Flask("Snippets Service")

cors = CORS(app, resources={r"/*": {"origins": "*"}})

settings = loadSettings("setting.json")

snippets_store = SnippetsStore(host=settings["database"]["host"],
                               port=settings["database"]["port"],
                               user=settings["database"]["user"],
                               password=settings["database"]["password"],
                               database=settings["database"]["database"])

snippets_store.init_store()

snippets_service = SnippetsService(snippets_store)

oidclient = OpenIdClient(required_scopes=["snippetsapi"], accepted_issuers=[settings["issuer"]], audience="snippetsapi")

is_user_jwt_policy = RequiredClaimsPolicy(claims_validators=[ClaimValueValidator("role", "user")])


@app.route("/snippets", methods=["GET"])
@oidclient.jwt_required
def get_snippets():
    try:
        title = request.args.get('title', type=str, default="")
        keywords = request.args.get('keywords', type=str, default="")
        limit = request.args.get('limit', type=int, default=25)
        skip = request.args.get('skip', type=int, default=0)
        mine = request.args.get('mine', type=bool, default=False)
    except Exception as err:
        return bad_request(err)

    if mine and not is_user_jwt_policy.is_authorized(g.jwt):
        return bad_request("Must use a User JWT to use argument mine=true")

    if keywords is not None and len(keywords) > 0:
        keywords = keywords.split(';')

    user_subject = None
    if mine:
        user_subject = g.jwt["sub"]

    result = snippets_service.get_snippets(title, skip, limit, keywords, user_subject)

    return jsonify(result)

@app.route("/snippets/<snippet_id>", methods=["GET", "DELETE"])
@oidclient.jwt_required
def get_or_delete_snippet(snippet_id):

    if request.method == "DELETE":
        if is_user_jwt_policy.is_authorized(g.jwt):
            snippets_service.delete_snippet(snippet_id, g.jwt["sub"])
            return 204
        else:
            return 403, "Forbidden"


    snippet = snippets_service.get_snippet(snippet_id)

    if snippet is None:
        return not_found("snippet {0} not found".format(snippet_id))

    return jsonify(snippet)


@app.route("/snippets/create", methods=["POST"])
@oidclient.jwt_required
def create_snippets():

    if not is_user_jwt_policy.is_authorized(g.jwt):
        return forbidden()

    if "Content-Type" not in request.headers:
        return bad_request("Content-Type header is missing")

    if not request.headers["Content-Type"] == "application/json":
        return bad_request("Only application/json is accepted as Content-Type")

    snippet = request.json

    # testing required field
    if "title" not in snippet:
        return bad_request("Title is a required field")

    if "content" not in snippet:
        return bad_request("Content is a required field")

    result = snippets_service.add_snippet(snippet["title"], snippet["content"], g.jwt["sub"], snippet["keywords"])

    return jsonify(result), 201


@app.route("/keywords", methods=["GET"])
@oidclient.jwt_required
def get_keywords():
    return jsonify(snippets_service.get_all_keywords())


if __name__ == '__main__':
    app.run(port=5002)