import json
from logging import getLogger
import pydash as _

logger = getLogger(__name__)

import requests
from requests.exceptions import ConnectionError

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

        #TODO handle API ERRORS
        if api_response.status_code == 201:
            return None
        
        elif api_response.status_code == 200:
            return api_response.json()
        
        #TODO
        elif api_response.json().get("error")["error"] == 1:
            raise StorageNotFoundError(api_response.json().get("error")["message"])
        elif api_response.json().get("error")["error"] == 2:
            raise StorageNotFoundError(api_response.json().get("error")["message"])
        else:
            logger.error(api_response.json())
            raise APIError(api_response.json())
              
    @BaseAPIAdaptor.service_status_decorator
    def create_workspace_storage(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name']
    ) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage"

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(
                {"storage": {"name": storage_name} }
            ),
        )

        return self.__handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def delete_workspace_storage(self, 
        workspace_id: str, 
        storage_name: str
    ) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage/?storage_name={storage_name}"
        
        api_response = self.make_api_request(
            requests.delete,
            _url,
        )
        return self.__handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def list_workspace_storage(self, 
        workspace_id: str,
    ) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage"

        api_response = self.make_api_request(
            requests.get,
            _url,
        )
        return self.__handle_response(api_response)      
    
    @BaseAPIAdaptor.service_status_decorator
    def list_workspace_storage_object(self, 
        workspace_id: str, 
        storage_name: str,
        storage_prefix: str,
    ) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage/{storage_name}?prefix={storage_prefix}"

        api_response = self.make_api_request(
            requests.get,
            _url,
        )
        return self.__handle_response(api_response)
    
    def generate_credentials(self, workspace_id :str, storage_name: str) -> dict:

        _url = f"{self.host}/workspace/{workspace_id}/storage/credentials"

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(
                {"name": storage_name}
            ),            
        )
        return self.__handle_response(api_response)