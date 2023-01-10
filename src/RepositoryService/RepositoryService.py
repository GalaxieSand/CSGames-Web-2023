from flask import Flask, request, jsonify, send_file, render_template, g
from OpenIdClient import OpenIdClient, ClaimValueValidator, RequiredClaimsPolicy
from RestAPI import Responses
from flask_cors import CORS
from Services.RepositoryService import RepositoryService, loadSettings, initialize_database
import io
import os
from SwaggerDefinition import SwaggerDefinition

app = Flask("Repositories Service")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

settings = loadSettings("setting.json")

admin_policy = RequiredClaimsPolicy(claims_validators=[ClaimValueValidator("role", "Admin")])

oidclient = OpenIdClient(required_scopes=["repoapi"], accepted_issuers=[settings["issuer"]], audience="repoapi")

repository_store = initialize_database(settings)
repository_service = RepositoryService(repository_store, settings["repositories_root"], settings["redis"]["host"], settings["redis"]["port"], settings["cache_ttl"])

swagger_def = SwaggerDefinition(app)
rest = swagger_def.api_definition


@app.route("/", methods=["GET"])
def root():
    return render_template('index.html', base_uri=settings["site_url"])


@rest.api_method(route="/authors",
                 methods=['GET'],
                 spec=swagger_def.methods["/authors"])
@oidclient.jwt_required
def get_authors():
    try:
        skip = request.args.get('skip', default=0, type=int)
        limit = request.args.get('limit', default=25, type=int)
        filter = request.args.get('filter', default="*", type=str)
    except Exception as ex:
        print(ex)
        return Responses.bad_request()

    if limit > 1000:
        limit = 1000

    return jsonify(repository_service.get_authors(skip, limit, filter))


@rest.api_method(route="/authors/<author_id>/repositories",
                 methods=['GET'],
                 spec=swagger_def.methods["/authors/<author_id>/repositories"])
@oidclient.jwt_required
def get_author_repositories(author_id):
    try:
        skip = request.args.get('skip', default=0, type=int)
        limit = request.args.get('limit', default=25, type=int)
    except Exception as ex:
        print(ex)
        return Responses.bad_request()

    if limit > 1000:
        limit = 1000

    return jsonify(repository_service.get_author_repositories(author_id, skip, limit))


@rest.api_method(route="/repositories",
                 methods=['GET'],
                 spec=swagger_def.methods["/repositories"])
@oidclient.jwt_required
def get_repositories():
    try:
        skip = request.args.get('skip', default=0, type=int)
        limit = request.args.get('limit', default=25, type=int)
        filter = request.args.get('filter', default="*", type=str)
    except Exception as ex:
        print(ex)
        return Responses.bad_request()

    if limit > 1000:
        limit = 1000

    return jsonify(repository_service.get_repositories(skip, limit, filter))


@rest.api_method(route="/repositories/<repository_id>",
                 methods=['GET'],
                 spec=swagger_def.methods["/repositories/<repository_id>"])
@oidclient.jwt_required
def get_repository(repository_id):

    resp = repository_service.get_repository(repository_id)
    if resp is None:
        return Responses.not_found()

    return jsonify(resp)


@rest.api_method(route="/repositories/<repository_id>/commits",
                 methods=['GET'],
                 spec=swagger_def.methods["/repositories/<repository_id>/commits"])
@oidclient.jwt_required
def get_repository_commits(repository_id):
    try:
        skip = request.args.get('skip', default=0, type=int)
        limit = request.args.get('limit', default=25, type=int)
        branch = request.args.get('branch', default="master", type=str)
    except Exception as ex:
        print(ex)
        return Responses.bad_request()
    if limit > 1000:
        limit = 1000

    resp = repository_service.get_repository_commits(repository_id, skip, limit, branch)
    if resp is None:
        return Responses.not_found()

    return jsonify(resp)


@rest.api_method(route="/repositories/<repository_id>/blob/commits",
                 methods=['GET'],
                 spec=swagger_def.methods["/repositories/<repository_id>/blob/commits"])
@oidclient.jwt_required
def get_repository_blob_commits(repository_id):
    try:
        branch = request.args.get('branch', default="HEAD", type=str)
        filepath = request.args.get('filepath', default=None, type=str)
    except Exception as ex:
        print(ex)
        return Responses.bad_request()

    if filepath is None:
        return Responses.bad_request("Missing filepath")

    resp = repository_service.get_repository_blob_commits(repository_id, filepath, branch)
    if resp is None:
        return Responses.not_found()

    return jsonify(resp)


@rest.api_method(route="/repositories/<repository_id>/tree",
                 methods=['GET'],
                 spec=swagger_def.methods["/repositories/<repository_id>/tree"])
@oidclient.jwt_required
def get_repository_tree(repository_id):
    try:
        path = request.args.get('path', default=".", type=str)
        branch = request.args.get('branch', default="master", type=str)
    except Exception as ex:
        print(ex)
        return Responses.bad_request()
    resp = repository_service.get_repository_tree(repository_id, branch, path)
    if resp is None:
        return Responses.not_found()
    return jsonify(resp)


@rest.api_method(route="/repositories/<repository_id>/diff",
                 methods=['GET'], 
                 spec=swagger_def.methods["/repositories/<repository_id>/diff"])
@oidclient.jwt_required
def get_repository_diff(repository_id):
    try:
        filepath = request.args.get('filepath', default=None, type=str)
        commit = request.args.get('commit', default="HEAD^", type=str)
        commit2 = request.args.get('commit2', default="HEAD", type=str)
    except Exception as ex:
        print(ex)
        return Responses.bad_request()

    if len(commit) == 0:
        return Responses.bad_request()

    resp = repository_service.get_diff(repository_id, commit, commit2, filepath)
    if resp is None:
        return Responses.not_found()

    return resp, 200


@rest.api_method(route="/repositories/<repository_id>/blob",
                 methods=['GET'],
                 spec=swagger_def.methods["/repositories/<repository_id>/blob"])
@oidclient.jwt_required
def get_repository_file(repository_id):
    try:
        filepath = request.args.get('filepath', default="", type=str)
        branch = request.args.get('branch', default="master", type=str)
    except Exception as ex:
        print(ex)
        return Responses.bad_request()

    if len(filepath) == 0:
        return Responses.bad_request()

    resp = repository_service.get_repository_file(repository_id, filepath, branch)
    if resp is None:
        return Responses.not_found()

    return send_file(io.BytesIO(resp), mimetype="application/octet-stream", as_attachment=True, attachment_filename=os.path.basename(filepath))


@rest.api_method(route="/topics",
                 methods=["GET"],
                 spec=swagger_def.methods["/topics"])
@oidclient.jwt_required
def get_topics():
    return jsonify(repository_service.get_all_topics())

# not used in prod
"""@rest.api_method(route="/repositories/import",
                 methods=['POST'],
                 spec=swagger_def.methods["/repositories/import"])
@oidclient.jwt_required
def import_repositories():
    if not admin_policy.is_authorized(g.jwt):
        return Responses.forbidden()

    data = request.json
    if "name" in data and "source_url" in data:
        repository_id = repository_store.add_repository(data["name"], data["source_url"])
        return jsonify({"id" : repository_id}), 201

    return Responses.bad_request()"""


if __name__ == '__main__':
    app.run(port=5001)
