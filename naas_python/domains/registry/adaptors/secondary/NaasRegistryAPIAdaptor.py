import os
import json

import requests

from naas_python import logger
from naas_python.domains.registry.RegistrySchema import (
    IRegistryAdaptor,
    RegistryAPIAdaptorError,
)
from requests.exceptions import ConnectionError


class NaasAPIAdaptorBase(IRegistryAdaptor):
    host = os.environ.get("NAAS_SPACE_API_HOST", "http://api.naas.ai")

    def __init__(self) -> None:
        super().__init__()

    def _check_service_status(self):
        """
        Check the status of the service API before executing other methods.
        """
        try:
            api_response = requests.get(f"{self.host}")

            if api_response.status_code == 200:
                logger.debug("Service status: Available")
                return True  # Service is available

            else:
                logger.debug("Service status: Unavailable")
                return False  # Service is not available

        except ConnectionError:
            logger.debug(f"Unable to connect to {self.host}")
            return False  # Service is not available

    @staticmethod
    def service_status_decorator(func):
        def wrapper(self, *args, **kwargs):
            if self._check_service_status():
                return func(self, *args, **kwargs)
            else:
                return "Service is unavailable"

        return wrapper

    def make_api_request(
        self, method, url, token=None, payload=None, body=None, headers={}
    ):
        if token:
            headers.update({"Authorization": f"Bearer {token}"})
        try:
            if payload:
                response = method(url, json=payload, headers=headers)
            if body:
                response = method(url, data=body, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad response status
            return response
        except requests.ConnectionError as e:
            raise RegistryAPIAdaptorError(
                f"Server seems to be unavailable at {self.host} or not running"
            ) from e
        except requests.HTTPError as e:
            raise RegistryAPIAdaptorError(f"HTTP error: {e}") from e


class NaasRegistryAPIAdaptor(NaasAPIAdaptorBase):
    def __init__(self):
        super(NaasAPIAdaptorBase).__init__()

    def handle_api_response(self, response, expected_status, json_extractor):
        if response.status == expected_status:
            return json_extractor(json.loads(response.read().decode()))
        elif response.status == 422:
            error = json.loads(response.read().decode())["detail"]
            raise ValueError(f"Validation Error: {error}")
        elif response.status == 404:
            raise ValueError("Not Found")
        elif response.status == 409:
            error = json.loads(response.read().decode())["detail"]
            raise ValueError(f"Conflict: {error}")
        elif response.status == 500:
            raise ValueError("Internal Server Error")
        else:
            raise ValueError(f"Unexpected status code: {response.status}")

    @NaasAPIAdaptorBase.service_status_decorator
    def create_registry(self, name, **kwargs):
        api_response = self.make_api_request(
            requests.post,
            f"{self.host}/registry",
            body=json.dumps({"name": name}),
            token=kwargs.get("token", os.environ.get("NAAS_TOKEN")),
        )

        return self.handle_create_response(api_response)

    @NaasAPIAdaptorBase.service_status_decorator
    def get_registry_by_name(self, name, self_param, **kwargs):
        api_response = self.make_api_request(
            requests.get,
            f"{self.host}/registry/{name}?self={self_param}",
            token=kwargs.get("token", os.environ.get("NAAS_TOKEN")),
        )
        return self.handle_get_response(api_response)

    @NaasAPIAdaptorBase.service_status_decorator
    def list_registries(self, **kwargs):
        api_response = self.make_api_request(
            requests.get,
            f"{self.host}/registry?page_size=100&page_number=0",
            token=kwargs.get("token", os.environ.get("NAAS_TOKEN")),
        )
        return self.handle_get_response(api_response)

    @NaasAPIAdaptorBase.service_status_decorator
    def delete_registry(self, name, self_param, delete_data, **kwargs):
        api_response = self.make_api_request(
            requests.delete,
            f"{self.host}/registry/{name}?self={self_param}",
            payload=json.dumps(delete_data),
            token=kwargs.get("token", os.environ.get("NAAS_TOKEN")),
        )
        return self.handle_delete_response(api_response)

    @NaasAPIAdaptorBase.service_status_decorator
    def get_registry_credentials(self, name, self_param, **kwargs):
        api_response = self.make_api_request(
            requests.get,
            f"{self.host}/registry/{name}/credentials?self={self_param}",
            token=kwargs.get("token", os.environ.get("NAAS_TOKEN")),
        )
        return self.handle_get_credentials_response(api_response)

    def handle_create_response(self, api_response):
        return self.handle_api_response(api_response, 201, lambda json_body: json_body)

    def handle_get_response(self, api_response):
        return self.handle_api_response(api_response, 200, lambda json_body: json_body)

    def handle_delete_response(self, api_response):
        return self.handle_api_response(api_response, 204, lambda json_body: None)

    def handle_get_credentials_response(self, api_response):
        return self.handle_api_response(api_response, 200, lambda json_body: json_body)
