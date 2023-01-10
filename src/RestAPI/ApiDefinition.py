from functools import wraps
from flasgger import Flasgger
from .HTTP import HTTP
import yaml


class CustomFlasgger(Flasgger):
    def __init__(self, app=None, config=None, sanitizer=None, template=None,
            template_file=None, decorators=None, validation_function=None,
            validation_error_handler=None, parse=False):
        Flasgger.__init__(self, app,
                          config=config,
                          sanitizer=sanitizer,
                          template=template,
                          template_file=template_file,
                          decorators=decorators,
                          validation_function=validation_function,
                          validation_error_handler=validation_error_handler,
                          parse=parse)

    def get_apispecs(self, endpoint='apispec_1'):
        # override to remove fields not compliant with OpenAPI 3.0
        data = Flasgger.get_apispecs(self, endpoint)
        if 'definitions' in data:
            data.pop('definitions')

        return data


class ApiDefinition:

    def __init__(self, flask_app, title="MyAPI", description="", version="1.0", security=None, swagger_route="/swagger_1.json", swagger_ui_route="/swagger/", schemes=['https'], openapi="3.0.0", schema_components={}):
        self.flask_app = flask_app
        self.security = security
        self.title = title
        self.description = description
        self.version = version

        self.schema_components = {}

        self.flask_app.config['SWAGGER'] = {
            'title': title,
            'uiversion': 3
        }

        self.flasgger_config = Flasgger.DEFAULT_CONFIG.copy()

        self.flasgger_config['specs'][0]['endpoint'] = "swagger_1"
        self.flasgger_config['specs'][0]['route'] = swagger_route
        self.flasgger_config['specs_route'] = swagger_ui_route
        self.flasgger_config['openapi'] = openapi

        self.flasgger_config['info'] = {
            "title": title,
            "description": description,
            "version": version
        }

        for schema_name in schema_components:
            yaml_schema = schema_components[schema_name].get_definition()
            yaml_object = yaml.load(yaml_schema, Loader=yaml.Loader)
            self.schema_components[schema_name] = yaml_object

        self.flasgger_template = {
            "security": [],
            "components": {
                "schemas": self.schema_components,
                "securitySchemes": {

                }
            }
        }

        if self.security is not None:
            self.flasgger_template['components']['securitySchemes'][self.security.scheme] = self.security.definition
            self.flasgger_template['security'].append({self.security.scheme: []})

        self.flasgger = CustomFlasgger(flask_app, config=self.flasgger_config, template=self.flasgger_template)

    def api_method(self, route, methods=[HTTP.Methods.GET], spec=None):
        def decorator(f):
            if spec is not None:
                f.__doc__ = spec.render_doc(f.__name__)

            @wraps(f)
            def wrap(*args, **kwargs):
                self.flask_app.route("/")
                return f(*args, **kwargs)

            return self.flask_app.route(route, methods=methods)(wrap)
        return decorator
