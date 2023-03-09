from .ApiSchema import ApiSchema, ApiSchemaConstant


class ApiObjectSchema(ApiSchema):
    def __init__(self, properties=[], ref=None):
        ApiSchema.__init__(self, ApiSchemaConstant.DT_Object)
        self.properties = properties
        self.ref = ref

    def get_definition(self, indent=0):
        indent_str = ""
        for n in range(indent):
            indent_str += " "
        defs = ""

        if self.ref is not None:
            defs += "{0}$ref: '#{1}'".format(indent_str, self.ref)
            return defs

        defs = "{0}type: object\n".format(indent_str)
        defs += "{0}properties:\n".format(indent_str)

        required_props = []

        for prop in self.properties:
            defs += prop.get_definition(indent+2)

            if prop.required:
                required_props.append(prop.name)

        if len(required_props) > 0:
            defs += "{0}required:\n".format(indent_str)
            for req_prop in required_props:
                defs += "{0}- {1}\n".format(indent_str, req_prop)

        return defs
