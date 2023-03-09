from .ApiSchema import ApiSchemaConstant

class ApiParameter:
    def __init__(self, name, param_in, description="", required=False, type=ApiSchemaConstant.DT_String, format=None):
        self.name = name
        self.param_in = param_in
        self.description = description
        self.required = required
        self.type = type
        self.format = format
