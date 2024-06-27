import json
import os
from os import getenv
import logging

import requests
from requests.exceptions import ConnectionError

from naas_python.domains.space.SpaceSchema import (
    ISpaceAdaptor,
    SpaceConflictError,
    SpaceNotFound,
    SpaceValidationError,
)
from naas_python.utils.domains_base.secondary.BaseAPIAdaptor import BaseAPIAdaptor


class NaasSpaceAPIAdaptor(BaseAPIAdaptor, ISpaceAdaptor):
    def __init__(self):
        super().__init__()

    @BaseAPIAdaptor.service_status_decorator
    def create_space(self, name, domain, containers) -> dict:
        _url = f"{self.host}/space/"

        logging.debug(f"create request url: {_url}")

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(
                {"name": name, "domain": domain, "containers": containers}
            ),
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_create_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def get_space_by_name(self, name):
        _url = f"{self.host}/space/{name}"
        logging.debug(f"get request url: {_url}")

        api_response = self.make_api_request(requests.get, f"{self.host}/space/{name}")

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )

        return self._handle_get_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def list_spaces(self) -> dict:    

        _url = f"{self.host}/space/"

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
    def update_space(self, name, domain, containers) -> dict:
        payload = {
            "containers": containers,
        }

        if domain:
            payload["domain"] = domain

        _url = f"{self.host}/space/{name}"

        logging.debug(f"update request url: {_url}")

        api_response = self.make_api_request(
            requests.put,
            _url,
            payload=json.dumps(payload),
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_get_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def delete_space(self, name) -> dict:
        _url = f"{self.host}/space/{name}"
        logging.debug(f"delete request url: {_url}")

        api_response = self.make_api_request(
            requests.delete,
            _url,
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_delete_response(api_response)

    def _handle_create_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 201:
            return api_response.json().get("space")

        elif api_response.status_code == 409:
            raise SpaceConflictError(
                f"Unable to create space: Conflict, {api_response.json().get('message')}",
            )

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )

            raise SpaceValidationError(
                f"Unprocessable Entity: '{component}', {error}",
            )

        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['message']}"
            )

    def _handle_list_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 200:
            return api_response.json().get("spaces")

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )

            raise SpaceValidationError(
                f"Unprocessable Entity: '{component}', {error}",
            )

        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['message']}"
            )

    def _handle_get_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 200:
            return api_response.json().get("space")

        elif api_response.status_code == 404:
            raise SpaceNotFound(
                f"Unable to find space: {api_response.json().get('message')}",
            )

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )

            raise SpaceValidationError(
                f"Unprocessable Entity: '{component}', {error}",
            )

        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['message']}"
            )

    def _handle_delete_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 200:
            return api_response.json().get("space")

        elif api_response.status_code == 404:
            raise SpaceNotFound(
                f"Unable to find space: {api_response.json().get('message')}",
            )

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )

            raise SpaceValidationError(
                f"Unprocessable Entity: '{component}', {error}",
            )

        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['message']}"
            )

    def _handle_update_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 200:
            return api_response.json().get("space")

        elif api_response.status_code == 404:
            raise SpaceNotFound(
                f"Unable to find space: {api_response.json().get('message')}",
            )

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )

            raise SpaceValidationError(
                f"Unprocessable Entity: '{component}', {error}",
            )

        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['message']}"
            )
