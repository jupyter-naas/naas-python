import json
import os
from os import getenv
import logging
logging.basicConfig(level=logging.DEBUG)

from typing import List

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

    @BaseAPIAdaptor.service_status_decorator
    def create_secret(self, name, value) -> dict:
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
        return self._handle_create_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def get(self, name):
        _url = f"{self.host}/secret/{name}"
        logging.debug(f"get request url: {_url}")

        api_response = self.make_api_request(requests.get, f"{self.host}/secret/{name}")

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )

        return self._handle_get_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def list_secrets(self, page_size, page_number) -> List[Secret]: 
           
        _url = f"{self.host}/secret/"
        # _token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmM2NmZWU2Ny0xMzQ0LTQzYWQtYmQxZC1hMTFmOTJiYWIyZDcifQ.j6zHzkpTmKq5eNiIF7Bkdho8ciaqGrRBnrolnssu9kk"
        payload = {"page_size": page_size, "page_number": page_number}
        _payload = json.dumps(payload)

        # print(f"url:{_url}")
        logging.debug(f"list request url: {_url}")
        api_response = self.make_api_request(
            requests.get,
            url=_url,
            # _token,
            payload=_payload,
            # headers=_headers
        )
        # print(f"api_response:{api_response}")
        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )

        # print(f"Request URL: {api_response.url} :: status_code: {api_response.status_code}")

        secrets = self._handle_list_response(api_response)['secrets']

        # Small version
        secretList : List[Secret] = [Secret(name=i['name'], value=i['value'] ) for i in secrets]

        # Long vesrsion
        secretList : List[Secret] = []
        for i in secrets:
            secretList.append(Secret(name=i['name'], value=i['value']))

        # print(secretList)

        return secretList

    # @BaseAPIAdaptor.service_status_decorator
    # def update_secret(self, name, domain, containers) -> dict:
    #     payload = {
    #         "containers": containers,
    #     }

    #     if domain:
    #         payload["domain"] = domain

    #     _url = f"{self.host}/secret/{name}"

    #     logging.debug(f"update request url: {_url}")

    #     api_response = self.make_api_request(
    #         requests.put,
    #         _url,
    #         payload=json.dumps(payload),
    #     )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_get_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def delete_secret(self, name) -> dict:
        _url = f"{self.host}/secret/{name}"
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
            # print(api_response.json().get("error"))
            return api_response.json().get("error")

        elif api_response.status_code == 409:
            raise SecretConflictError(
                f"Unable to create secret: Conflict, {api_response.json().get('error')}",
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

    def _handle_list_response(self, api_response: requests.Response) -> dict:
        print(f"_handle_list_response: {api_response.json()}")

        if api_response.status_code == 200:
            return api_response.json()

        elif api_response.status_code == 422:
            # validation code from FastAPI is 422
            # gather attribute name and error message
            print(f"uprocessable:{api_response.json()}")
            component, error = (
                api_response.json()["detail"][0]["loc"][1],
                api_response.json()["detail"][0]["msg"],
            )

            raise SecretValidationError(
                f"Unprocessable Entity: '{component}', {error}",
            )

        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()['message']}"
            )

    def _handle_get_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 200:
            return api_response.json()

        elif api_response.status_code == 404:
            raise SecretNotFound(
                f"Unable to find secret: {api_response.json().get('message')}",
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
                f"An unknown error occurred: {api_response.json()['message']}"
            )

    def _handle_delete_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 200:
            return api_response.json().get("Secret")

        elif api_response.status_code == 404:
            raise SecretNotFound(
                f"Unable to find secret: {api_response.json().get('message')}",
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
                f"An unknown error occurred: {api_response.json()['message']}"
            )

    # def _handle_update_response(self, api_response: requests.Response) -> dict:
    #     if api_response.status_code == 200:
    #         return api_response.json().get("secret")

    #     elif api_response.status_code == 404:
    #         raise SecretNotFound(
    #             f"Unable to find secret: {api_response.json().get('message')}",
    #         )

    #     elif api_response.status_code == 422:
    #         # validation code from FastAPI is 422
    #         # gather attribute name and error message
    #         component, error = (
    #             api_response.json()["detail"][0]["loc"][1],
    #             api_response.json()["detail"][0]["msg"],
    #         )

    #         raise SecretValidationError(
    #             f"Unprocessable Entity: '{component}', {error}",
    #         )

    #     else:
    #         raise Exception(
    #             f"An unknown error occurred: {api_response.json()['message']}"
    #         )
