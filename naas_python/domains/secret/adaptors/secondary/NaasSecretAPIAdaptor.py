import json
import os
from os import getenv
import logging
logging.basicConfig(level=logging.ERROR)

from typing import List
import pydash as _

import requests
from requests.exceptions import ConnectionError

from naas_python.domains.secret.SecretSchema import (
    ISecretAdaptor,
    SecretConflictError,
    SecretNotFound,
    SecretValidationError,
    Secret
)
from naas_python.utils.domains_base.secondary.BaseAPIAdaptor import BaseAPIAdaptor


class NaasSecretAPIAdaptor(BaseAPIAdaptor, ISecretAdaptor):
    def __init__(self):
        super().__init__()


    def _handle_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 201:
            return None
        
        elif api_response.status_code == 200:
            return api_response.json()

        elif api_response.status_code == 409:
            raise SecretConflictError(
                f"Unable to create secret: Conflict, {api_response.json().get('error')}",
            )

        elif api_response.status_code == 404:
            raise SecretNotFound(
                f"Unable to find secret.",
            )

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )

            raise SecretValidationError(
                f"Unprocessable Entity: '{component}', {error}",
            )

        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['error']}"
            )

    @BaseAPIAdaptor.service_status_decorator
    def create_secret(self, name: str, value: str) -> None:
        _url = f"{self.host}/secret/"

        logging.debug(f"create request url: {_url}")

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(
                {"secret": {"name": name, "value": value} }
            ),
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        self._handle_response(api_response)
        return None

    @BaseAPIAdaptor.service_status_decorator
    def bulk_create(self, secrets_list: List[Secret]) -> None:
        _url = f"{self.host}/secret/bulk"
        
        logging.debug(f"create request url: {_url}")

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(
                secrets_list
            ),
        )
        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        self._handle_response(api_response)
        return None

    @BaseAPIAdaptor.service_status_decorator
    def get_secret(self, name:str) -> Secret:
        _url = f"{self.host}/secret/{name}"
        logging.debug(f"get request url: {_url}")

        api_response = self.make_api_request(requests.get, f"{self.host}/secret/{name}")

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )

        response_payload = self._handle_response(api_response)

        return Secret(name=_.get(response_payload, 'secret.name'), value=_.get(response_payload, 'secret.value'))

    @BaseAPIAdaptor.service_status_decorator
    def list_secrets(self, page_size: int, page_number: int) -> List[Secret]: 
        _url = f"{self.host}/secret/"
        payload = {"page_size": page_size, "page_number": page_number}

        logging.debug(f"list request url: {_url}")
        api_response = self.make_api_request(
            requests.get,
            url=_url,
            payload=json.dumps(payload)
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )

        secrets = self._handle_response(api_response)['secrets']
        secretList : List[Secret] = [Secret(name=i['name'], value=i['value'] ) for i in secrets]
        return secretList

    @BaseAPIAdaptor.service_status_decorator
    def delete_secret(self, name) -> None:
        _url = f"{self.host}/secret/{name}"
        logging.debug(f"delete request url: {_url}")

        api_response = self.make_api_request(
            requests.delete,
            _url,
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_response(api_response)