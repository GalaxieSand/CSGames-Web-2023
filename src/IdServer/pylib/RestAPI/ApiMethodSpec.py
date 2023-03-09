

class ApiMethodSpec:
    def __init__(self, summary="", parameters=[], responses=[], tags=[], request_body=None, produces=[], consumes=[]):
        self.summary = summary
        self.parameters = parameters
        self.responses = responses
        self.tags = tags
        self.request_body = request_body
        self.produces = produces
        self.consumes = consumes

    def render_doc(self, operation_id=None):
        tags = ""
        for t in self.tags:
            tags += "  - {0}\n".format(t)

        request_body = ""
        if self.request_body is not None:
            request_body += "requestBody:\n"
            request_body += self.request_body.get_definition()

        parameters = ""
        if len(self.parameters) > 0:
            parameters = "parameters:\n"

            for param in self.parameters:
                required = "false"
                if param.required:
                    required = "true"

                parameters += "- name: {0}\n".format(param.name)
                parameters += "  in: {0}\n".format(param.param_in)
                parameters += "  description: {0}\n".format(param.description)
                if param.required:
                    parameters += "  required: {0}\n".format(required)

                parameters += "  schema:\n"
                parameters += "    type: string\n"

                if param.format is not None:
                    parameters += "  format: {0}\n".format(param.format)

        if operation_id is not None:
            operation_id = "operationId: {0}\n".format(operation_id)
        else:
            operation_id = ""

        responses = ""
        for r in self.responses:
            responses += r.get_definition(2)

        spec = """
{0}
---
{1}
tags:
{2}
{3}
{4}
responses:
{5}
""".format(self.summary, operation_id, tags, request_body, parameters, responses)
        #print(spec)
        return spec

