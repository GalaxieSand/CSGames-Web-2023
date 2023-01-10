from RestAPI import *


class SwaggerDefinition:
    def __init__(self, app):
        self.app = app
        self.title = "Repositories Service"
        self.version = "1.0"
        self.security = SecurityDefinition.BearerAuthorizationHeader()

        self.schema_components = {
            "RepositoryResult": ApiObjectSchema(properties=[
                ApiSchemaProperty("id", ApiSchemaProperty.DT_Integer, description="Repository Identifier"),
                ApiSchemaProperty("name", ApiSchemaProperty.DT_String, description="Repository name"),
                # ApiSchemaProperty("remote_git", ApiSchemaProperty.DT_String, description="Remote address of the repository"),
                ApiSchemaProperty("license", ApiSchemaProperty.DT_String, description="Project license"),
                ApiSchemaProperty("description", ApiSchemaProperty.DT_String, description="Project description")
            ]),
            "Repository":
                ApiObjectSchema(properties=[
                    ApiSchemaProperty("id", ApiSchemaProperty.DT_Integer, description="Repository Identifier"),
                    ApiSchemaProperty("name", ApiSchemaProperty.DT_String, description="Repository name"),
                    ApiSchemaProperty("topics", ApiSchemaProperty.DT_Array,
                                      description="Array of topics related to this repository",
                                      items=["type: string"]),
                    # ApiSchemaProperty("remote_git", ApiSchemaProperty.DT_String, description="Remote address of the repository"),
                    ApiSchemaProperty("contributors", ApiSchemaProperty.DT_Array,
                                      items=["$ref: '#/components/schemas/Author'"]),
                    ApiSchemaProperty("branches", ApiSchemaProperty.DT_Array,
                                      description="All branches of the repository",
                                      items=["type: string"]),
                    ApiSchemaProperty("tags", ApiSchemaProperty.DT_Array, description="All tags of the repository",
                                      items=["type: string"]),
                    ApiSchemaProperty("license", ApiSchemaProperty.DT_String, description="Project license"),
                    ApiSchemaProperty("languages", ApiSchemaProperty.DT_Array,
                                      description="All languages of the repository", items={"type: string"}),
                    ApiSchemaProperty("description", ApiSchemaProperty.DT_String, description="Project description")
                ]),
            "Author": ApiObjectSchema(properties=[
                ApiSchemaProperty("id", ApiSchemaProperty.DT_String, description="Author Id"),
                ApiSchemaProperty("name", ApiSchemaProperty.DT_String, description="Author Name"),
                ApiSchemaProperty("email", ApiSchemaProperty.DT_String, description="Author Email"),
                ApiSchemaProperty("subject", ApiSchemaProperty.DT_String,
                                  description="Unique User Id across all services")
            ]),
            "TreeEntry": ApiObjectSchema(properties=[
                ApiSchemaProperty("filename", ApiSchemaProperty.DT_String, description="Entry filename"),
                ApiSchemaProperty("tree_hash", ApiSchemaProperty.DT_String, description="Tree hash"),
                ApiSchemaProperty("type", ApiSchemaProperty.DT_String, description="Entry type blob or tree")
            ]),
            "Commit": ApiObjectSchema(properties=[
                ApiSchemaProperty("author", ApiSchemaProperty.DT_String, description="Author of the commit"),
                ApiSchemaProperty("date", ApiSchemaProperty.DT_String, description="Commit Hash"),
                ApiSchemaProperty("message", ApiSchemaProperty.DT_String, description="Commit Message"),
            ])
        }

        self.api_definition = ApiDefinition(self.app,
                                            title=self.title,
                                            version=self.version,
                                            security=self.security,
                                            schema_components=self.schema_components)

        # Methods definition

        self.methods = {
            "/authors": ApiMethodSpec(
                summary="Search through authors. JWT is required to access that end point",
                parameters=[ApiParameter(name="skip",
                                         param_in="query",
                                         type=ApiSchemaProperty.DT_Integer,
                                         description="Number of elements to skip, default to 0"),
                            ApiParameter(name="limit",
                                         param_in="query",
                                         type=ApiSchemaProperty.DT_Integer,
                                         description="Maximum of elements returned, default to 25"),
                            ApiParameter(name="filter",
                                         param_in="query",
                                         type=ApiSchemaProperty.DT_String,
                                         description="Filter author name that matches that string")],
                tags=["Authors"],
                responses=[ApiResponseSpec(HTTP.StatusCode.OK,
                                           schema=ApiObjectSchema(properties=[
                                               ApiSchemaProperty("totalMatches",
                                                                 type=ApiSchemaConstant.DT_Integer,
                                                                 description="Total records matching criteria"),
                                               ApiSchemaProperty("authors",
                                                                 type=ApiSchemaConstant.DT_Array,
                                                                 items=["$ref: '#/components/schemas/Author'"])
                                           ]),
                                           description="Operation was successful"),
                           ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                           ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                           ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/authors/<author_id>/repositories": ApiMethodSpec(
                summary="Search through author's repositories. JWT is required to access that end point",
                parameters=[
                    ApiParameter(name="author_id", param_in="path", type=ApiSchemaProperty.DT_Integer, required=True,
                                 description="Author Id"),
                    ApiParameter(name="skip", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                 description="Number of elements to skip, default to 0"),
                    ApiParameter(name="limit", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                 description="Maximum of elements returned, default to 25")],
                tags=["Authors"],
                responses=[ApiResponseSpec(HTTP.StatusCode.OK,
                                           schema=ApiObjectSchema(properties=[
                                               ApiSchemaProperty("totalMatches", type=ApiSchemaConstant.DT_Integer,
                                                                 description="Total records matching criteria"),
                                               ApiSchemaProperty("repositories", type=ApiSchemaConstant.DT_Array,
                                                                 items=[
                                                                     "$ref: '#/components/schemas/RepositoryResult'"])
                                           ]),
                                           description="Operation was successful"),
                           ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                           ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                           ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/repositories": ApiMethodSpec(
                summary="Search through repositories. JWT is required to access that end point",
                parameters=[ApiParameter(name="skip", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Number of elements to skip, default to 0"),
                            ApiParameter(name="limit", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Maximum of elements returned, default to 25"),
                            ApiParameter(name="filter", param_in="query", type=ApiSchemaProperty.DT_String,
                                         description="Filter repositories that matches that string")],
                tags=["Repository"],
                responses=[ApiResponseSpec(HTTP.StatusCode.OK,
                                           schema=ApiObjectSchema(properties=[
                                               ApiSchemaProperty("totalMatches", type=ApiSchemaConstant.DT_Integer,
                                                                 description="Total records matching criteria"),
                                               ApiSchemaProperty("repositories", type=ApiSchemaConstant.DT_Array,
                                                                 items=[
                                                                     "$ref: '#/components/schemas/RepositoryResult'"])
                                           ]),
                                           description="Operation was successful"),
                           ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                           ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                           ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/repositories/<repository_id>": ApiMethodSpec(
                summary="Get a repository. JWT is required to access that end point",
                parameters=[ApiParameter(name="repository_id", param_in="path", required=True,
                                         type=ApiSchemaProperty.DT_Integer, description="Id of the repository")],
                tags=["Repository"],
                responses=[ApiResponseSpec(HTTP.StatusCode.OK,
                                           schema=ApiObjectSchema(properties=
                                                                  [ApiSchemaProperty("repository",
                                                                                     type=ApiSchemaConstant.DT_Array,
                                                                                     items=[
                                                                                         "$ref: '#/components/schemas/Repository'"])
                                                                   ]),
                                           description="Operation was successful"),
                           ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                           ApiResponseSpec(HTTP.StatusCode.NotFound, "Not Found"),
                           ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                           ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/repositories/<repository_id>/commits": ApiMethodSpec(
                summary="Browse through repository commits. JWT is required to access that end point",
                parameters=[ApiParameter(name="repository_id", param_in="path", type=ApiSchemaProperty.DT_Integer,
                                         required=True, description="Id of the repository"),
                            ApiParameter(name="skip", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Number of commits to skip"),
                            ApiParameter(name="limit", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Maximum number of results, 25 by default"),
                            ApiParameter(name="branch", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Selected branch, master by default")
                            ],
                tags=["Repository"],
                responses=[ApiResponseSpec(HTTP.StatusCode.OK,
                                           schema=ApiObjectSchema(properties=[ApiSchemaProperty("commits",
                                                                                                description="An array of commits",
                                                                                                type=ApiSchemaProperty.DT_Array,
                                                                                                items=[
                                                                                                    "$ref: '#/components/schemas/Commit'"])]),
                                           description="Operation was successful"),
                           ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                           ApiResponseSpec(HTTP.StatusCode.NotFound, "Not Found"),
                           ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                           ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/repositories/<repository_id>/blob/commits": ApiMethodSpec(
                summary="Browse through commits related to a blob. JWT is required to access that end point",
                parameters=[ApiParameter(name="repository_id", param_in="path", required=True,
                                         type=ApiSchemaProperty.DT_Integer, description="Id of the repository"),
                            ApiParameter(name="branch", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Selected branch, HEAD by default"),
                            ApiParameter(name="filepath", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Path to blob", required=True)
                            ],
                tags=["Repository"],
                responses=[ApiResponseSpec(HTTP.StatusCode.OK,
                                           schema=ApiObjectSchema(properties=[ApiSchemaProperty("commits",
                                                                                                description="An array of commits",
                                                                                                type=ApiSchemaProperty.DT_Array,
                                                                                                items=[
                                                                                                    "$ref: '#/components/schemas/Commit'"])]),
                                           description="Operation was successful"),
                           ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                           ApiResponseSpec(HTTP.StatusCode.NotFound, "Not Found"),
                           ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                           ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/repositories/<repository_id>/tree": ApiMethodSpec(
                summary="Browse through repository trees. JWT is required to access that end point",
                parameters=[ApiParameter(name="repository_id", param_in="path", type=ApiSchemaProperty.DT_Integer,
                                         required=True, description="Id of the repository"),
                            ApiParameter(name="branch", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Selected branch, master by default"),
                            ApiParameter(name="path", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Path of the repository for the wanted tree, by default .")
                            ],
                tags=["Repository"],
                responses=[ApiResponseSpec(HTTP.StatusCode.OK,
                                           schema=ApiObjectSchema(properties=[ApiSchemaProperty("tree",
                                                                                                description="An array of tree entries",
                                                                                                type=ApiSchemaProperty.DT_Array,
                                                                                                items=[
                                                                                                    "$ref: '#/components/schemas/TreeEntry'"])]),
                                           description="Operation was successful"),
                           ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                           ApiResponseSpec(HTTP.StatusCode.NotFound, "Not Found"),
                           ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                           ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/repositories/<repository_id>/diff": ApiMethodSpec(
                summary="Generate a diff between two point. JWT is required to access that end point",
                parameters=[ApiParameter(name="repository_id", param_in="path", type=ApiSchemaProperty.DT_Integer,
                                         required=True, description="Id of the repository"),
                            ApiParameter(name="filepath", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Path of the in the repository"),
                            ApiParameter(name="commit", param_in="query", type=ApiSchemaProperty.DT_String,
                                         description="First commit, if no second commit is provided HEAD will be used as a second one.", ),
                            ApiParameter(name="commit2", param_in="query", type=ApiSchemaProperty.DT_String,
                                         description="Second commit")],
                tags=["Repository"],
                responses=[
                    ApiResponseSpec(HTTP.StatusCode.OK, content="application/octet-stream", description="Blob content"),
                    ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                    ApiResponseSpec(HTTP.StatusCode.NotFound, "Not Found"),
                    ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                    ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/repositories/<repository_id>/blob": ApiMethodSpec(
                summary="Retrieve a blob. JWT is required to access that end point",
                parameters=[ApiParameter(name="repository_id", param_in="path", type=ApiSchemaProperty.DT_Integer,
                                         required=True, description="Id of the repository"),
                            ApiParameter(name="filepath", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Path of the in the repository"),
                            ApiParameter(name="branch", param_in="query", type=ApiSchemaProperty.DT_Integer,
                                         description="Selected branch, master by default"),
                            ],
                tags=["Repository"],
                responses=[
                    ApiResponseSpec(HTTP.StatusCode.OK, content="application/octet-stream", description="Blob content"),
                    ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                    ApiResponseSpec(HTTP.StatusCode.NotFound, "Not Found"),
                    ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                    ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/repositories/import": ApiMethodSpec(
                summary="Import a new repository with https uri. Require Admin role",
                request_body=ApiRequestBody(required=True, content_type="application/json",
                                            schema=ApiObjectSchema(properties=[
                                                ApiSchemaProperty("source_url",
                                                                  description="Id of the client used for authentication",
                                                                  required=True),
                                                ApiSchemaProperty("name",
                                                                  description="Secret of the client used",
                                                                  required=True)])),
                consumes=["application/json"],
                tags=["Repository"],
                responses=[ApiResponseSpec(HTTP.StatusCode.Created, content="application/json", schema=ApiObjectSchema({
                    ApiSchemaProperty(name="id", type=ApiSchemaProperty.DT_Integer, description="Repository Id")
                }), description="Repository was added"),
                           ApiResponseSpec(HTTP.StatusCode.BadRequest, "Bad Request"),
                           ApiResponseSpec(HTTP.StatusCode.NotFound, "Not Found"),
                           ApiResponseSpec(HTTP.StatusCode.Unauthorized, "Not Authorized"),
                           ApiResponseSpec(HTTP.StatusCode.Forbidden, "Forbidden")]),

            "/topics": ApiMethodSpec(
                summary="List all availables topics",
                tags=["Topics"],
                responses=[ApiResponseSpec(HTTP.StatusCode.OK, description="Topics", schema=ApiObjectSchema([
                    ApiSchemaProperty("topics", type=ApiSchemaProperty.DT_Array, items=["type: string"])
                ]
                ))]
            )

        }
