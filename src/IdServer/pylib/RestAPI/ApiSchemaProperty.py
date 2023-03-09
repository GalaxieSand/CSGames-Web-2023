

class ApiSchemaProperty:
    (DT_String, DT_Number, DT_Integer, DT_Boolean, DT_Array, DT_Object) = ("string", "number", "integer", "boolean", "array", "object")

    def __init__(self, name, type=DT_String, description=None, default=None, format=None, required=False, items=[]):
        self.name = name
        self.type = type
        self.default = default
        self.format = format
        self.required = required
        self.description = description
        self.items = items

    def get_definition(self, indent=0):
        indent_str = ""
        for i in range(indent):
            indent_str += " "
        defs = ""
        defs += "{0}{1}:\n".format(indent_str, self.name)
        defs += "{0}  type: {1}\n".format(indent_str, self.type)

        if self.description is not None:
            defs += "{0}  description: {1}\n".format(indent_str, self.description)

        if self.default is not None:
            defs += "{0}  default: {1}\n".format(indent_str, self.default)

        if self.format is not None:
            defs += "{0}  format: {1}\n".format(indent_str, self.format)

        if self.type == self.DT_Array and len(self.items) > 0:
            defs += "{0}  items:\n".format(indent_str)
            for item in self.items:
                defs += "{0}    {1}\n".format(indent_str, item)

        return defs