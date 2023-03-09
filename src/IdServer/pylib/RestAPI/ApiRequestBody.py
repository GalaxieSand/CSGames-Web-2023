from .HTTP import HTTP


class ApiRequestBody:
    def __init__(self, content_type=HTTP.MimeType.UrlFormEncoded, schema=None, required=False):
        self.content_type = content_type
        self.schema = schema
        self.required = required

    def get_definition(self):
        defs = ""
        if self.required:
            defs += "    required: true\n"

        defs += "    content:\n"
        defs += "      {0}:\n".format(self.content_type)
        if self.schema is not None:
            defs += "        schema:\n"
            defs += self.schema.get_definition(10)

        return defs
