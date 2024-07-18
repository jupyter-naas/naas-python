import os
from logging import getLogger
import pydash as _
import json

logger = getLogger(__name__)

import requests

from naas_python.utils.domains_base.secondary.BaseAPIAdaptor import BaseAPIAdaptor

from naas_python.domains.storage.StorageSchema import (
    Storage,
    IStorageAdaptor,
)
from naas_python.domains.storage.StorageSchema import APIError, StorageNotFoundError

class NaasStorageAPIAdaptor(BaseAPIAdaptor, IStorageAdaptor):
    def __init__(self):
        super().__init__()                  

    def __handle_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 201:
            return api_response.json()
        elif api_response.status_code == 200:
            return api_response.json()
        elif api_response.status_code == 404:
            raise StorageNotFoundError(api_response.json().get("error")["message"])
        elif api_response.json().get("error")["code"] == 0 and api_response.json().get("error")["message"] == "Success":
            raise api_response.json()
        else:
            logger.error(api_response.json())
            raise APIError(api_response.json())
              
    @BaseAPIAdaptor.service_status_decorator
    def create(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name']
    ) -> dict:
        _url = f"{self.host}/workspace/{workspace_id}/storage/"

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload={
                "storage": 
                    {"name": storage_name}
            },
        )
        return self.__handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def delete(self, 
        workspace_id: str, 
        storage_name: str
    ) -> dict:
        _url = f"{self.host}/workspace/{workspace_id}/storage/?storage_name={storage_name}"
        
        api_response = self.make_api_request(
            requests.delete,
            _url,
        )
        return self.__handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def list(self, 
        workspace_id: str,
    ) -> dict:
        _url = f"{self.host}/workspace/{workspace_id}/storage/"

        api_response = self.make_api_request(
            requests.get,
            _url,
        )
        return self.__handle_response(api_response)      
    
    @BaseAPIAdaptor.service_status_decorator
    def list_objects(self, 
        workspace_id: str, 
        storage_name: str,
        storage_prefix: str,
    ) -> dict:
        _url = f"{self.host}/workspace/{workspace_id}/storage/{storage_name}?prefix={storage_prefix}"

        api_response = self.make_api_request(
            requests.get,
            _url,
        )
        return self.__handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def delete_object(self, 
        workspace_id: str, 
        storage_name: str,
        object_name: str,
    ) -> dict:
        object=os.path.basename(object_name)
        prefix=os.path.dirname(object_name)
        _url = f"{self.host}/workspace/{workspace_id}/storage/{storage_name}?prefix={prefix}&object={object}"

        api_response = self.make_api_request(
            requests.delete,
            _url,
        )
        return self.__handle_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def create_credentials(self, workspace_id : str, storage_name: Storage.__fields__['name']) -> dict:

        _url = f"{self.host}/workspace/{workspace_id}/storage/credentials/"

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload={
                "name": storage_name
            }
            ,            
        )
        return self.__handle_response(api_response)