import os
from typing import Any, Union
import logging
import json

import requests
from cachetools.func import ttl_cache
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError, NewConnectionError

from naas_python.utils.domains_base.authorization import NaasSpaceAuthenticatorAdapter
from naas_python.utils.exceptions import NaasException


class ServiceAuthenticationError(NaasException):
    pass


class ServiceStatusError(NaasException):
    pass


class BaseAPIAdaptor(NaasSpaceAuthenticatorAdapter):
    host = os.environ.get("NAAS_PYTHON_API_BASE_URL", "https://api.naas.ai")
    # host = os.environ.get("NAAS_PYTHON_API_BASE_URL", "http://localhost:8000")
    # Cache name is the name of the calling module
    cache_name = __name__
    cache_expire_after = 60  # Cache expires after 60 seconds

    def __init__(self) -> None:
        # Base authenticator class
        super().__init__()

    @ttl_cache(maxsize=1, ttl=cache_expire_after)
    def _check_service_status(self):
        """
        Check the status of the service API before executing other methods.
        """
        try:
            logging.debug(f"API Base URL: {self.host}")

            api_response = requests.get(f"{self.host}")

            logging.debug(
                f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
            )

            if api_response.status_code == 200:
                return True  # Service is available

            return False  # Service is not available

        except (ConnectionError, NewConnectionError, MaxRetryError) as e:
            raise ServiceStatusError(
                f"Unable to connect to [cyan]{self.host}[/cyan]. The service is currently unavailable. Please try again within a few minutes.",
                e,
            )

    @staticmethod
    def  service_status_decorator(func):
        def wrapper(self, *args, **kwargs):
            self._check_service_status()
            return func(self, *args, **kwargs)

        return wrapper

    def make_api_request(
        self,
        method: Union[
            requests.get, requests.post, requests.patch, requests.put, 
            # requests.delete
        ],
        url: str,
        token: str = None,
        payload: dict = {},
        headers: dict = {},
    ):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        # Will be updated using the new authorization validators
        if token:
            headers.update({"Authorization": f"Bearer {token}"})
        else:
            headers.update({"Authorization": f"Bearer {self.jwt_token()}"})

        try:
            api_response = method(url, data=payload, headers=headers)
            api_response.raise_for_status()
            return api_response

        except requests.exceptions.HTTPError as e:
            _response = api_response.json()
            if api_response.status_code == 401:
                _message = ""
                if "error_message" in _response:
                    _message = _response["error_message"]
                elif "detail" in _response:
                    _message = _response["detail"]
                else:
                    _message = "Unauthorized"
                raise ServiceAuthenticationError(
                    f"Unable to authenticate with the service. Please check your credentials and try again. Details: {_message}",
                    e,
                )
            elif api_response.status_code == 500:
                _message = ""
                if "error_message" in _response:
                    _message = _response["error_message"]
                elif "detail" in _response:
                    _message = _response["detail"]
                else:
                    _message = "Internal Server Error"
                raise ServiceStatusError(_message, e)
            else:
                # Other status codes will be handled by the calling method
                return api_response
