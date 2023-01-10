from HttpTests import TestCase, HttpErrorStatusCodeValidator, ResponseStatusCodeValidator, JsonContentResponseValidator
from OpenIdClient import OpenIdClient
import json

test_snippet_id = None
snippet_data = {"title": "My first test snippet",
                "content": "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
                "keywords": [
                    "cpp",
                    "test"]
                }

def validate_create_snippet(json_content):
    if "id" in json_content:
        global test_snippet_id
        test_snippet_id = json_content["id"]
        return True, ""

    return False, "Id field not found"

def validate_get_snippet(json_content):
    global snippet_data

    for k in snippet_data:
        if k in json_content:
            print("\t{0} is present in response".format(k))
            if k != "keywords" and snippet_data[k] == json_content[k]:
                print("\t{0} value is the same".format(k))



if __name__ == '__main__':
    issuer = "http://localhost:5000"

    oidclient = OpenIdClient(audience=issuer, accepted_issuers=[issuer])

    hostname = 'http://127.0.0.1:5002'
    service_account_jwt = oidclient.get_service_token(issuer, 'tenant1', 'dev')
    user_jwt = oidclient.get_user_token(issuer, 'tenant1', 'dev', '6aa028949359', 'gitimport')

    snippet_data = {"title": "My first test snippet",
                    "content": "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
                    "keywords": [
                        "cpp",
                        "test"
                        ]
                    }

    test_suites = []

    test_suites.append(TestCase("/snippets without JWT should return 401",
                                "{0}/snippets".format(hostname),
                                http_error_validators=[HttpErrorStatusCodeValidator(401)]))

    test_suites.append(TestCase("/snippets with Service Account JWT should return 200",
                                "{0}/snippets".format(hostname),
                                headers={"Authorization": "Bearer {0}".format(service_account_jwt["access_token"])},
                                response_validators=[ResponseStatusCodeValidator(200)]))

    test_suites.append(TestCase("/snippets using mine=True with Service Account JWT should return 400",
                                "{0}/snippets?mine=true".format(hostname),
                                headers={"Authorization": "Bearer {0}".format(service_account_jwt["access_token"])},
                                http_error_validators=[HttpErrorStatusCodeValidator(400)]))

    test_suites.append(TestCase("/snippets using mine=True with User JWT should return 200",
                                "{0}/snippets?mine=true".format(hostname),
                                headers={"Authorization": "Bearer {0}".format(user_jwt["access_token"])},
                                response_validators=[ResponseStatusCodeValidator(200)]))

    test_suites.append(TestCase("/snippets/create with good body and an user token should return 201",
                                "{0}/snippets/create".format(hostname),
                                method="POST",
                                request_body=json.dumps(snippet_data).encode('utf-8'),
                                headers={
                                    "Authorization": "Bearer {0}".format(user_jwt["access_token"]),
                                    "Content-Type": "application/json"
                                },
                                response_validators=[ResponseStatusCodeValidator(201),
                                                     JsonContentResponseValidator(validate_create_snippet)]
                                ))



    for test_case in test_suites:
        test_case.run()
        test_outcome = "Passed"

        if not test_case.success:
            test_outcome = "Failed"

        print("Test {0} has {1}".format(test_case.name, test_outcome))
        if len(test_case.messages) > 0:
            for m in test_case.messages:
                print(m)





    # seconds set of tests
    print("2")