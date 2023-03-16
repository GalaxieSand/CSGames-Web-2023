from flask import Flask, jsonify, request, g, render_template
from flask_cors import CORS
import Models
from Services.OpenIdException import OpenIdException
from Services.OpenIdService import OpenIdService, loadSettings
from HelperFunctions import initialize_database
from functools import wraps
import time
import jwt
from RestAPI import ApiDefinition, ApiMethodSpec, SecurityDefinition, ApiResponseSpec, ApiObjectSchema, ApiRequestBody, ApiSchemaProperty, ApiParameter, HTTP, ApiSchemaConstant


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

rest = ApiDefinition(app, title="Identity Server", version="1.0",
                     security=SecurityDefinition.BearerAuthorizationHeader(),
                     description="Service providing user creation and authentication")

clientStore = None
userStore = None
settings = loadSettings("setting.json")
openidService = None
clientStore = initialize_database(settings)
clientStore.init_store()

openidService = OpenIdService(settings["issuer"],
                              clientStore,
                              clientStore,
                              settings["token"]["privateKeyPath"],
                              settings["token"]["signingCertificatePath"])
openidService.init_service()


class Authorization:
    def __init__(self, audience, public_key, scope_required=[]):
        self.audience = audience
        self.public_key = public_key
        self.scope_required = scope_required

    def jwt_required(self, f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'authorization' not in request.headers:
                return "Not Authorized", 401
            try:
                bearer = request.headers["authorization"].replace('Bearer ', '')
                decoded_token = jwt.decode(bearer,
                                           self.public_key,
                                           audience=self.audience)

                if decoded_token["exp"] < int(time.time()):
                    return "Not Authorized", 401

                g.jwt = decoded_token

                if len(self.scope_required) > 0:
                    for scope in self.scope_required:
                        if scope not in g.jwt['scope']:
                            return "Forbidden", 403

            except Exception as err:
                print(err)
                return "Not Authorized", 401
            return f(*args, **kwargs)
        return wrap


authz = Authorization(openidService.openIdConfiguration.wellKnown.issuer,
                      openidService.openIdConfiguration.privateKey.publickey().exportKey('PEM'),
                      ['idserver'])


def bad_request(message):
    return message, 400

@app.route("/")
def home():
    return render_template('index.html', base_uri=settings["issuer"])


@rest.api_method("/user/create", methods=["POST"], spec=ApiMethodSpec(
    "Create an user under a specific client",
    responses=[ApiResponseSpec(201, schema=ApiObjectSchema(properties=[
                                               ApiSchemaProperty("sub",
                                                         type=ApiSchemaConstant.DT_String,
                                                         description="Created user subject",
                                                         format="guid")
                                           ]),
                                           description="Operation was successful"),
               ApiResponseSpec(400, description="Invalid Request")],
    consumes=['x-url-encoded-form'],
    tags=["Users"],
    parameters=[],
    request_body=ApiRequestBody(required=True, schema=ApiObjectSchema(properties=[
         ApiSchemaProperty("username", description="Username of the user to create", required=True),
         ApiSchemaProperty("password", description="Password of the user to create", required=True)])
    )
))

@authz.jwt_required
def create_user():
    username = request.form.get("username")
    password = request.form.get("password")

    if username is not None and password is not None:
        client = openidService.clients[g.jwt['client_id']]

        if "role" in g.jwt:
            if g.jwt["role"] == "Importer":
                return openidService.userService.create_user_without_client(username, password)

        if "is_service" not in g.jwt:
            return "Forbidden", 403

        return openidService.userService.create_user(client, username, password)
    else:
        return "Bad Request", 400

@rest.api_method("/connect/token",
    methods=["POST"],
    spec=ApiMethodSpec(
        "Generate a token for a specific Client. You can also use the password grant to get a user JWT.",
        responses=[ApiResponseSpec(200, description="Token was emitted", schema=ApiObjectSchema([
            ApiSchemaProperty("access_token", description="Json Web Token generated"),
            ApiSchemaProperty("ttl", type=ApiSchemaProperty.DT_Integer, description="Time to live"),
            ApiSchemaProperty("scopes", type=ApiSchemaProperty.DT_Array, description="Scopes of the token", items=["type: string"])
        ])),
                   ApiResponseSpec(400, "Request is invalid")],
        consumes=[HTTP.Consumes.UrlEncodedForm],
        tags=["Token"],
        request_body=ApiRequestBody(required=True, schema=ApiObjectSchema(properties=[
                    ApiSchemaProperty("client_id",
                                      description="Id of the client used for authentication",
                                      required=True),
                    ApiSchemaProperty("client_secret",
                                      description="Secret of the client used",
                                      required=True),
                    ApiSchemaProperty("grant_type",
                                      description="Grant Type used for authentication (client_credentials or password)",
                                      default="client_credentials",
                                      required=True),
                    ApiSchemaProperty("scope",
                                      description="Scope access asked, if left empty, all scopes availables will be assigned"),
                    ApiSchemaProperty("username",
                                      description="Username used if grant_type is password"),
                    ApiSchemaProperty("password",
                                      description="Password used if grant_type is password")
            ])
        )
    )
)

def connect_token():
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    grant_type = request.form.get("grant_type")
    username = request.form.get("username")
    password = request.form.get("password")
    scopes = request.form.get("scope")

    if scopes is not None and len(scopes) > 0:
        scopes = scopes.split(' ')
    else:
        scopes = []

    if grant_type is None:
        return bad_request("grant_type is required")
    if client_id is None:
        return bad_request("client_id is required")

    if grant_type == Models.OpenIdConstants.GrantType.ClientCredentials:
        if client_secret is None:
            return bad_request("client_secret is required")
    elif grant_type == Models.OpenIdConstants.GrantType.Password:
        if username is None or password is None or client_secret is None:
            return bad_request("username and password is required")

    if username is not None and len(username) == 0:
        username = None
    if password is not None and len(password) == 0:
        password = None

    try:
        token_information = openidService.create_token(client_id, client_secret, grant_type, scopes, username, password)
    except OpenIdException as err:
        print(err.message)
        return bad_request(err.message)

    return jsonify(token_information)


@app.route("/.well-known/openid-configuration", methods=['GET'])
def open_id_configuration():
    return jsonify(openidService.openIdConfiguration.wellKnown.__dict__)


@app.route("/.well-known/openid-configuration/jwks", methods=['GET'])
def jwks():
    keys = []
    for k in openidService.openIdConfiguration.jsonWebKeySet:
        keys.append(k.to_json())

    return jsonify({
        "keys": keys
    })


if __name__ == '__main__':
    app.run()
