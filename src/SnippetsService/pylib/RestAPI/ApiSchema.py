
class ApiSchemaConstant:
    (DT_String, DT_Number, DT_Integer, DT_Boolean, DT_Array, DT_Object) = ("string", "number", "integer", "boolean", "array", "object")

    def __init__(self):
        pass


class ApiSchema:
    def __init__(self, type=ApiSchemaConstant.DT_String, items=[]):
        self.type = type
        self.items = items

    def get_definition(self, indent=0):
        indent_str = ""
        for n in range(indent):
            indent_str += " "
        defs = "{0}type: {1}\n".format(indent_str, self.type)

        if self.type == ApiSchemaConstant.DT_Array and len(self.items) > 0:
            defs += "{0}items:\n".format(indent_str)
            for item in self.items:
                defs += "{0}  {1}\n".format(indent_str, item)

        return defs

