from ...SpaceSchema import ISpaceAdaptor

import requests
import os

from requests.exceptions import ConnectionError
from rich import print
from naas_python import logger


class NaasSpaceAPIAdaptorException(BaseException):
    pass


class NaasSpaceAPIAdaptor(ISpaceAdaptor):
    def __init__(self):
        super().__init__()
        self.host = os.environ.get("NAAS_SPACE_API_HOST", "http://localhost:8000")

    def _check_service_status(self):
        """
        Check the status of the service API before executing other methods.
        """
        try:
            api_response = requests.get(f"{self.host}/space/status")

            if api_response.status_code == 200:
                logger.debug("Service status: Available")
                return True  # Service is available

            else:
                logger.debug("Service status: Unavailable")
                return False  # Service is not available

        except ConnectionError:
            logger.debug(f"Unable to connect to {self.host}")
            return False  # Service is not available

    def service_status_decorator(func):
        def wrapper(self, *args, **kwargs):
            if self._check_service_status():
                return func(self, *args, **kwargs)
            else:
                return "Service is unavailable"

        return wrapper

    def make_api_request(self, method, url, payload=None):
        try:
            logger.debug(f"Making API request: {method.__name__} {url}")
            api_response = method(url, json=payload)
            return api_response

        except ConnectionError:
            logger.debug(f"Failed to make API request: {method.__name__} {url}")
            return f"Server seems to be unavailable at {self.host} or not running"

    def handle_api_response(self, api_response, success_code, success_handler):
        if api_response.status_code == success_code:
            logger.debug("API response: Success")
            return success_handler(api_response.json())

        elif api_response.status_code == 409:
            logger.debug("API response: Conflict")
            json_body = api_response.json()
            return f"Conflict: '{json_body.get('reason')}', Message: {json_body.get('message')}"

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )
            logger.debug(
                f"API response: Unprocessable Entity :: '{component}' :: '{error}'"
            )
            return f"Unprocessable Entity: '{component}' :: '{error}'"

        elif api_response.status_code == 500:
            logger.debug("API response: Internal Server Error")
            return "Internal Server Error"

        else:
            logger.debug(
                f"API response: Untracked Error :: {api_response.status_code} :: {api_response.json()}"
            )
            raise NaasSpaceAPIAdaptorException(
                f"An untracked error occurred on the API [{api_response.status_code}]"
            )

    def handle_create_response(self, api_response):
        return self.handle_api_response(
            api_response, 201, lambda json_body: json_body.get("space")
        )

    def handle_get_response(self, api_response):
        return self.handle_api_response(api_response, 200, lambda json_body: json_body)

    def handle_delete_response(self, api_response):
        return self.handle_api_response(
            api_response, 200, lambda json_body: "Space deleted successfully"
        )

    def handle_list_response(self, api_response):
        return self.handle_api_response(api_response, 200, lambda json_body: json_body)

    @service_status_decorator
    def create(
        self,
        **kwargs,
    ):
        """
        Create a space with the specified details.
        """
        payload = {}
        for key, value in kwargs.items():
            if value is not None:
                payload[key] = value

        api_response = self.make_api_request(
            method=requests.post, url=f"{self.host}/space/", payload=payload
        )
        return self.handle_create_response(api_response)

    @service_status_decorator
    def get(self, name: str, namespace: str):
        """
        Get a space with the specified name and namespace.
        """
        api_response = self.make_api_request(
            requests.get, f"{self.host}/space/{namespace}/{name}"
        )
        return self.handle_get_response(api_response)

    @service_status_decorator
    def add(self):
        return super().add()
