import json
import os
import sys

import requests
from requests.exceptions import ConnectionError

from naas_python.domains.registry.RegistrySchema import (
    IRegistryAdaptor,
    RegistryAPIAdaptorError,
)
from naas_python.utils.domains_base.secondary.BaseAPIAdaptor import BaseAPIAdaptor


class NaasRegistryAPIAdaptor(BaseAPIAdaptor, IRegistryAdaptor):
    def __init__(self):
        super().__init__()
        # TODO: will be moved to proper authorization utility function
        self._authorization_token = os.environ.get("NAAS_PYTHON_API_TOKEN")

    def handle_api_response(self, response, expected_status, json_extractor=None):
        status_actions = {
            expected_status: lambda: json_extractor(
                json.loads(response.read().decode())
            ),
            422: lambda: RegistryAPIAdaptorError(
                message=f"Validation Error: {json.loads(response.read().decode())['detail']}"
            ),
            404: lambda: RegistryAPIAdaptorError(
                message=f"Resource not found: {json.loads(response.read().decode())['detail']}"
            ),
            409: lambda: RegistryAPIAdaptorError(
                message=f"Conflict: {json.loads(response.read().decode())['detail']}"
            ),
        }

        action = status_actions.get(
            response.status,
            lambda: RegistryAPIAdaptorError(
                message=f"Untracked Error {json.loads(response.read().decode())}"
            ),
        )
        return action()

    @BaseAPIAdaptor.service_status_decorator
    def create_registry(self, name):
        try:
            api_response = self.make_api_request(
                requests.post,
                f"{self.host}/registry/",
                payload=json.dumps({"name": name}),
                token=self._authorization_token,
            )
            return self._handle_create_response(api_response)

        except RegistryAPIAdaptorError as e:
            e.pretty_print()
            sys.exit(1)
        except Exception as e:
            raise RegistryAPIAdaptorError(e) from e

    @BaseAPIAdaptor.service_status_decorator
    def get_registry_by_name(self, name):
        try:
            api_response = self.make_api_request(
                requests.get,
                f"{self.host}/registry/{name}",
                token=self._authorization_token,
            )
            return self._handle_get_response(api_response)
        except RegistryAPIAdaptorError as e:
            e.pretty_print()
            sys.exit(1)
        except Exception as e:
            raise RegistryAPIAdaptorError(e) from e

    @BaseAPIAdaptor.service_status_decorator
    def list_registries(self, page_size, page_number):
        try:
            api_response = self.make_api_request(
                requests.get,
                f"{self.host}/registry?page_size={page_size}&page_number={page_number}",
                token=self._authorization_token,
            )
            return self._handle_get_response(api_response)
        except RegistryAPIAdaptorError as e:
            e.pretty_print()
            sys.exit(1)
        except Exception as e:
            raise RegistryAPIAdaptorError(e) from e

    @BaseAPIAdaptor.service_status_decorator
    def delete_registry(self, name):
        try:
            api_response = self.make_api_request(
                requests.delete,
                f"{self.host}/registry/{name}",
                token=self._authorization_token,
            )
            return self._handle_delete_response(api_response)
        except RegistryAPIAdaptorError as e:
            e.pretty_print()
            sys.exit(1)
        except Exception as e:
            raise RegistryAPIAdaptorError(e) from e

    @BaseAPIAdaptor.service_status_decorator
    def get_registry_credentials(self, name):
        try:
            api_response = self.make_api_request(
                requests.get,
                f"{self.host}/registry/{name}/credentials",
                token=self._authorization_token,
            )
            return self._handle_get_credentials_response(api_response)
        except RegistryAPIAdaptorError as e:
            e.pretty_print()
            sys.exit(1)
        except Exception as e:
            raise RegistryAPIAdaptorError(e) from e

    def _handle_create_response(self, api_response):
        try:
            return self.handle_api_response(
                api_response, 201, lambda json_body: json_body
            )
        except RegistryAPIAdaptorError as e:
            raise RegistryAPIAdaptorError(e) from e

    def _handle_get_response(self, api_response):
        try:
            if api_response.status_code == 200:
                return self.handle_api_response(
                    api_response, 200, lambda json_body: json_body
                )
            else:
                return self.handle_api_response(api_response, api_response.status_code)
        except RegistryAPIAdaptorError as e:
            raise RegistryAPIAdaptorError(e) from e

    def _handle_delete_response(self, api_response):
        try:
            return self.handle_api_response(api_response, 204, lambda json_body: None)
        except RegistryAPIAdaptorError as e:
            raise RegistryAPIAdaptorError(e) from e

    def _handle_get_credentials_response(self, api_response):
        try:
            return self.handle_api_response(
                api_response, 200, lambda json_body: json_body
            )
        except RegistryAPIAdaptorError as e:
            raise RegistryAPIAdaptorError(e) from e
