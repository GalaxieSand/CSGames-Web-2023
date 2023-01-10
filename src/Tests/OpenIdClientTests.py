from OpenIdClient import OpenIdClient

def get_user_account_token():
    oidclient = OpenIdClient(audience="http://localhost:5000", accepted_issuers=["http://localhost:5000"])
    token = oidclient.get_user_token("http://localhost:5000", "tenant1", "dev", "617e99b1a74e", "gitimport")
    return token["access_token"]

def get_service_account_token():
    oidclient = OpenIdClient(audience="http://localhost:5000", accepted_issuers=["http://localhost:5000"])
    token = oidclient.get_service_token("http://localhost:5000", "tenant1", "dev")
    return token["access_token"]

if __name__ == '__main__':
    service_account_token = get_service_account_token()
    print(service_account_token)

    user_account_token = get_user_account_token()
    print(user_account_token)