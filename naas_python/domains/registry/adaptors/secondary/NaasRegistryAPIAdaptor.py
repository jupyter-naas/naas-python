import json
import logging

import requests

from naas_python.domains.registry.RegistrySchema import (
    IRegistryAdaptor,
    RegistryConflictError,
    RegistryNotFound,
    RegistryValidationError,
)
from naas_python.utils.domains_base.secondary.BaseAPIAdaptor import BaseAPIAdaptor


class NaasRegistryAPIAdaptor(BaseAPIAdaptor, IRegistryAdaptor):
    def __init__(self):
        super().__init__()
        # self.authenticator = NaasSpaceAuthenticatorAdapter()
        # self._authorization_token = self.authenticator.jwt_token

    @BaseAPIAdaptor.service_status_decorator
    def create_registry(self, name) -> dict:
        _url = f"{self.host}/registry/"

        logging.debug(f"create request url: {_url}")

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps({"name": name}),
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_create_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def get_registry_by_name(self, name) -> dict:
        _url = f"{self.host}/registry/{name}"
        logging.debug(f"get request url: {_url}")

        api_response = self.make_api_request(
            requests.get,
            f"{self.host}/registry/{name}",
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )

        return self._handle_get_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def list_registries(self, page_size, page_number) -> dict:
        _url = f"{self.host}/registry/?page_size={page_size}&page_number={page_number}"

        logging.debug(f"list request url: {_url}")

        api_response = self.make_api_request(
            requests.get,
            _url,
        )
        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_list_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def delete_registry(self, name) -> dict:
        _url = f"{self.host}/registry/{name}"
        logging.debug(f"delete request url: {_url}")

        api_response = self.make_api_request(
            requests.delete,
            _url,
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )

        return self._handle_delete_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def get_registry_credentials(self, name) -> dict:
        _url = f"{self.host}/registry/{name}/credentials"

        logging.debug(f"get credentials request url: {_url}")

        api_response = self.make_api_request(
            requests.get,
            _url,
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )

        return self._handle_get_credentials_response(api_response)

    def _handle_create_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 201:
            return api_response.json()

        elif api_response.status_code == 409:
            raise RegistryConflictError(
                f"Unable to create registry: {api_response.json()['error_message']}"
            )
        elif api_response.status_code == 422:
            raise RegistryValidationError(
                f"Unable to parse request: {api_response.json()['error_message']}"
            )
        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['error_message']}"
            )

    def _handle_list_response(self, api_response: requests.Response):
        if api_response.status_code == 200:
            return api_response.json()

        elif api_response.status_code == 404:
            raise RegistryNotFound(
                f"Error from server: {api_response.json()['error_message']}"
            )
        elif api_response.status_code == 422:
            raise RegistryValidationError(
                f"Unable to parse request: {api_response.json()['error_message']}"
            )
        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['error_message']}"
            )

    def _handle_get_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 200:
            return api_response.json()

        elif api_response.status_code == 404:
            raise RegistryNotFound(
                f"Error from server: {api_response.json()['error_message']}"
            )
        elif api_response.status_code == 422:
            raise RegistryValidationError(
                f"Unable to parse request: {api_response.json()['error_message']}"
            )
        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['error_message']}"
            )

    def _handle_delete_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 204:
            return {}

        elif api_response.status_code == 404:
            raise RegistryNotFound(
                f"Error from server: {api_response.json()['error_message']}"
            )
        elif api_response.status_code == 422:
            raise RegistryValidationError(
                f"Unable to parse request: {api_response.json()['error_message']}"
            )
        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['error_message']}"
            )

    def _handle_get_credentials_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 200:
            return api_response.json()

        elif api_response.status_code == 404:
            raise RegistryNotFound(
                f"Error from server: {api_response.json()['error_message']}"
            )
        elif api_response.status_code == 422:
            raise RegistryValidationError(
                f"Unable to parse request: {api_response.json()['error_message']}"
            )
        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['error_message']}"
            )
