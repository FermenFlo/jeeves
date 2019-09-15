import os
from jeeves.src.commands.utils import APIRequest
from uber_rides.auth import AuthorizationCodeGrant
from uber_rides.client import UberRidesClient


class UberRequest(APIRequest):
    def __init__(
        self, 
        client_id = os.environ['UBER_CLIENT_ID'],
        client_secret = os.environ['UBER_CLIENT_SECRET'],
        scopes = {'profile'},
        redirect_url = "http://localhost:8000/uber/connect"
        ):
        
        auth_flow = AuthorizationCodeGrant(
            client_id = client_id,
            scopes = scopes,
            client_secret = client_secret,
            redirect_url = redirect_url,
        )
        
        auth_url = auth_flow.get_authorization_url()
        print(auth_url)
        # session = auth_flow.get_session(redirect_url)
        # client = UberRidesClient(session)
        # credentials = session.oauth2credential


if __name__ == '__main__':
    ur = UberRequest()
