import os
import json

import requests
from naas_python import logger
from naas_python.domains.space.SpaceSchema import ISpaceAdaptor, SpaceAPIAdaptorError
from requests.exceptions import ConnectionError


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

    def make_api_request(self, method, url, token, payload=None):
        try:
            logger.debug(f"Making API request: {method.__name__} {url}")
            print(payload)
            if method == requests.post:
                api_response = method(
                    url, data=payload, headers={"Authorization": f"Bearer {token}"}
                )
            else:
                api_response = method(
                    url, json=payload, headers={"Authorization": f"Bearer {token}"}
                )
            return api_response

        except ConnectionError as e:
            logger.debug(f"Failed to make API request: {method.__name__} {url}")
            raise SpaceAPIAdaptorError(
                f"Server seems to be unavailable at {self.host} or not running",
            ) from e

    def handle_api_response(self, api_response, success_code, success_handler):
        if api_response.status_code == success_code:
            logger.debug("API response: Success")
            return success_handler(api_response.json())

        elif api_response.status_code == 400:
            logger.debug(
                f"{self.__class__.__name__}: {api_response.json().get('message')}"
            )
            raise SpaceAPIAdaptorError(
                message=f"Bad Request: {api_response.json().get('message')}",
            )

        elif api_response.status_code == 404:
            logger.debug(
                f"{self.__class__.__name__}: {api_response.json().get('message')}"
            )
            raise SpaceAPIAdaptorError(
                message=f"No resource matching the given criteria: {api_response.json().get('message')}",
            )

        elif api_response.status_code == 409:
            logger.debug("API response: Conflict")
            json_body = api_response.json()
            raise SpaceAPIAdaptorError(
                message=f"Conflict, {json_body.get('message')}",
            )

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )
            print(api_response.json())

            raise SpaceAPIAdaptorError(
                message=f"Unprocessable Entity: '{component}', {error}",
            )

        elif api_response.status_code == 500:
            raise SpaceAPIAdaptorError(
                message="Internal Server Error",
            )

        else:
            raise SpaceAPIAdaptorError(
                message=f"Untracked Error {api_response.json()}",
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
        name = kwargs.get("name")
        containers = kwargs.get("containers")
        token = kwargs.get("token")

        api_response = self.make_api_request(
            method=requests.post,
            url=f"{self.host}/space/",
            payload=json.dumps({"name": name, "containers": containers}),
            token=kwargs.get("token", os.environ.get("NAAS_TOKEN")),
        )
        return self.handle_create_response(api_response)

    @service_status_decorator
    def delete(self, name: str, namespace: str, token: str):
        """
        Delete a space with the specified name and namespace.
        """
        api_response = self.make_api_request(
            requests.delete,
            f"{self.host}/space/{name}?namespace={namespace}",
            token=token,
        )
        return self.handle_delete_response(api_response)

    @service_status_decorator
    def get(self, name: str, namespace: str, token: str):
        """
        Get a space with the specified name and namespace.
        """
        api_response = self.make_api_request(
            requests.get, f"{self.host}/space/{name}?namespace={namespace}", token=token
        )
        return self.handle_get_response(api_response)

    @service_status_decorator
    def list(self, namespace: str, token: str):
        """
        List all spaces in the specified namespace.
        """
        api_response = self.make_api_request(
            requests.get, f"{self.host}/space/list/{namespace}", token=token
        )
        return self.handle_list_response(api_response)

    @service_status_decorator
    def update(self, name: str, namespace: str, update_patch: dict, token: str):
        """
        Update a space with the specified name and namespace.
        """
        api_response = self.make_api_request(
            requests.post,
            f"{self.host}/space/{name}/update?namespace={namespace}",
            update_patch,
            token=token,
        )
        return self.handle_get_response(api_response)

    @service_status_decorator
    def add(self):
        return super().add()
