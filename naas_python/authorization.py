import os
from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

import jwt
import requests
from cachetools import TTLCache, cached

from naas_python.domains.space.SpaceSchema import ISpaceAdaptor, SpaceAPIAdaptorError


@dataclass
class NAASCredentials:
    token: str


# Cache for 15 minutes (900 seconds)
cache = TTLCache(maxsize=1, ttl=900)


class NaasSpaceAuthenticatorAdapter:
    """Adapter for authenticating with the NaaS authentication service."""

    def __init__(self):
        self.auth_host = "https://auth.naas.ai"
        self.auth_bearer_endpoint = f"{self.auth_host}/bearer/jupyterhubtoken"
        self.health_check_endpoint = f"{self.auth_host}/login/credentials/health"

        self.cache = cache

    def _check_auth_server_status(self):
        """Check if the authentication server is running and accessible."""
        try:
            response = requests.get(self.health_check_endpoint)
            return response.status_code == 200
        except requests.RequestException:
            return False

    @cached(cache)  # Use the @cached decorator here
    def _get_access_token(self, token):
        """Retrieve the access token from the authentication server."""
        URL = f"{self.auth_bearer_endpoint}?token={token}"
        response = requests.get(URL)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise ValueError("Failed to retrieve access token from auth server.")

    def get_access_token(self):
        """Get the access token for API authentication."""
        if not self._check_auth_server_status():
            raise ValueError("Auth server is not running or not accessible.")

        jupyterhub_token = os.getenv("TOKEN", "YOUR_JUPYTERHUB_TOKEN_HERE")
        decoded_token = jwt.decode(jupyterhub_token, algorithms=["HS256"], verify=False)
        exp_timestamp = decoded_token.get("exp")
        now = datetime.now(timezone.utc)
        remaining_time = exp_timestamp - now.timestamp()

        if remaining_time < 300:  # 300 seconds = 5 minutes
            self.cache.pop("access_token", None)
            return self._get_access_token(jupyterhub_token)

        return None


class NaasSpaceAPIAdaptor(ISpaceAdaptor):
    """Adapter for interacting with the NaaS Space API."""

    def __init__(self):
        super().__init__()
        self.host = os.environ.get("NAAS_SPACE_API_HOST", "http://localhost:8000")
        self.authenticator = NaasSpaceAuthenticatorAdapter()

    def make_api_request(self, method, url, token, payload=None):
        """Make an API request with proper authentication."""
        access_token = self.authenticator.get_access_token()

        try:
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


# TODO: For testing only. Remove this block of code before WIP is merged to develop.
if __name__ == "__main__":
    space_adaptor = NaasSpaceAPIAdaptor()

    try:
        space_adaptor.authenticator.get_access_token()
        # Perform other operations using the NaasSpaceAPIAdaptor class...
    except Exception as e:
        print(str(e))
