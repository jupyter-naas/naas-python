from .models.Asset import Asset

from naas_python.domains.asset.AssetSchema import (
    IAssetDomain,
    IAssetAdaptor,
    Asset,
    AssetCreation,
    AssetUpdate
)

class AssetDomain(IAssetDomain):
    adaptor: IAssetAdaptor

    def __init__(self, adaptor: IAssetAdaptor):
        self.adaptor = adaptor

    def create_asset(self, workspace_id:str, asset_creation:AssetCreation) -> Asset:
        asset = self.adaptor.create_asset(workspace_id, asset_creation)
        return asset
    
    def get_asset(self, workspace_id:str, asset_id:str) -> Asset:
        asset = self.adaptor.get_asset(workspace_id, asset_id)
        return asset

    # def get_asset_object(self, workspace_id:str, asset_id:str, password:str) -> dict:
    #     asset_url = self.adaptor.get_asset_object(workspace_id, asset_id, password)
    #     return asset_url

    def update_asset(self, workspace_id:str, asset_id:str, asset_update: AssetUpdate) -> dict:
        response = self.adaptor.update_asset(workspace_id, asset_id, asset_update)
        return response

    def delete_asset(self, workspace_id:str, asset_id:str) -> dict:
        response = self.adaptor.delete_asset(workspace_id, asset_id)
        return response