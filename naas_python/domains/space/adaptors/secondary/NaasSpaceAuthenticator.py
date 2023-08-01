import os
import requests
import json
import datetime
import time
from naas_python.domains.space.SpaceSchema import ISpaceAdaptor, SpaceAPIAdaptorError


from cachetools import cached, TTLCache

cache = TTLCache(maxsize=1, ttl=900)  # Cache for 15 minutes (900 seconds)


class NaasSpaceAuthenticatorAdapter:
    def __init__(self):
        self.auth_host = "https://auth.naas.ai"
        self.auth_bearer_endpoint = f"{self.auth_host}/bearer/jupyterhubtoken"
        self.health_check_endpoint = f"{self.auth_host}/login/credentials/health"

        self.cache = cache

    def _check_auth_server_status(self):
        try:
            response = requests.get(self.health_check_endpoint)
            return response.status_code == 200
        except requests.RequestException:
            return False

    @cached(cache)
    def _get_access_token(self, token):
        URL = "https://auth.naas.ai/bearer/jupyterhubtoken" + "?token=" + token
        response = requests.get(URL)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise ValueError("Failed to retrieve access token from auth server.")

    def get_access_token(self):
        # Check if the auth server is running and accessible
        if not self._check_auth_server_status():
            raise ValueError("Auth server is not running or not accessible.")

        # Get the JupyterHub token from the environment variable or provide it directly
        jupyterhub_token = os.getenv("TOKEN", "YOUR_JUPYTERHUB_TOKEN_HERE")

        # Retrieve and return the access token using the JupyterHub token
        return self._get_access_token(jupyterhub_token)


class NaasSpaceAPIAdaptor(ISpaceAdaptor):
    def __init__(self):
        super().__init__()
        self.host = os.environ.get("NAAS_SPACE_API_HOST", "http://localhost:8000")
        # self.host = "https://auth.naas.ai"

        # Create an instance of the NaasSpaceAuthenticatorAdapter
        self.authenticator = NaasSpaceAuthenticatorAdapter()

    def make_api_request(self, method, url, token, payload=None):
        # Retrieve the access token using the authenticator
        access_token = self.authenticator.get_access_token()

        try:
            # Make the API request with the access token in the headers
            headers = {"Authorization": f"Bearer {access_token}"}
            if method == requests.post:
                api_response = method(url, data=payload, headers=headers)
            else:
                api_response = method(url, json=payload, headers=headers)
            return api_response

        except ConnectionError as e:
            raise SpaceAPIAdaptorError(
                f"Failed to make API request: {method.__name__} {url}"
            ) from e


if __name__ == "__main__":
    # TODO: For testing only. Remove this block of code before WIP is merged to develop.
    # Initialize the NaasSpaceAPIAdaptor class
    space_adaptor = NaasSpaceAPIAdaptor()

    try:
        # Log in to the authentication service and fetch access token
        space_adaptor.authenticator.get_access_token()

        # Perform other operations using the NaasSpaceAPIAdaptor class...
    except Exception as e:
        print(str(e))
