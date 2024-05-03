import requests, json

import pydash as _

from naas_python.utils.domains_base.secondary.BaseAPIAdaptor import BaseAPIAdaptor

from naas_python.domains.asset.AssetSchema import (
    IAssetAdaptor,
    AssetConflictError,
    AssetNotFound,
    AssetRequestError,
    Asset,
    AssetCreation,
    AssetUpdate,
)

class NaasAssetAPIAdaptor(BaseAPIAdaptor, IAssetAdaptor):
    def __init__(self):
        super().__init__()
    
    def _handle_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 201:
            return None
        
        elif api_response.status_code == 200:
            return api_response.json()

        elif api_response.status_code == 409:
            raise AssetConflictError(api_response.json()['message'])
        
        elif api_response.status_code == 404:
            raise AssetNotFound(api_response.json()['message'])

        elif api_response.status_code == 400:
            raise AssetRequestError(api_response.json()['message'])

        elif api_response.status_code == 500:
            if 'code' in api_response.json() and api_response.json()['code'] == AssetError.UNEXPECTED_ERROR:
                raise AssetUnexpectedError(api_response.json()['message'])
            else:
                raise AssetInternalError(api_response.json()['message'])
        else:
            raise Exception(f"An unknown error occurred: {api_response.json()}")

    @BaseAPIAdaptor.service_status_decorator
    def create_asset(self, workspace_id:str, asset_creation:AssetCreation) -> Asset:
        _url = f"{self.host}/workspace/{workspace_id}/asset/"

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(asset_creation)
        )
        return self._handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def get_asset(self, workspace_id:str, asset_id:str) -> Asset:
        _url = f"{self.host}/workspace/{workspace_id}/asset/{asset_id}"
        api_response = self.make_api_request(
            requests.get,
            _url
        )
        return self._handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def update_asset(self, workspace_id:str, asset_id:str, asset_update: AssetUpdate) -> Asset:
        _url = f"{self.host}/workspace/{workspace_id}/asset/{asset_id}"
        api_response = self.make_api_request(
            requests.put,
            _url,
            payload=json.dumps(asset_update)
        )
        return self._handle_response(api_response)

    @BaseAPIAdaptor.service_status_decorator
    def delete_asset(self, workspace_id: str, asset_id: str) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/asset/{asset_id}"
        api_response = self.make_api_request(
            requests.delete,
            _url
        )
        return None