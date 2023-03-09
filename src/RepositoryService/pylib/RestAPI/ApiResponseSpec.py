from .ApiSchema import ApiSchemaConstant


class ApiResponseSpec:
    def __init__(self, status_code, description=None, schema=None, content="application/json"):
        self.status_code = status_code
        self.description = description
        self.schema = schema
        self.content = content

    def get_definition(self, indent=0):
        indent_str = ""
        for i in range(indent):
            indent_str += " "

        defs = "{0}  {1}:\n".format(indent_str, self.status_code)
        if self.description is not None:
            defs += "{0}    description: {1}\n".format(indent_str, self.description)

        if self.content is not None and self.schema is not None:
            defs += "{0}    content: \n".format(indent_str)
            defs += "{0}      {1}:\n".format(indent_str, self.content)
            defs += "{0}        schema:\n".format(indent_str, self.schema)
            defs += self.schema.get_definition(indent+10)

        return defs

