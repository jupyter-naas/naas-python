
from naas_python.domains.asset.AssetSchema import (
    IAssetDomain,
    IAssetPrimaryAdaptor,
    Asset,
    AssetCreation,
    AssetUpdate
)

class SDKAssetAdaptor(IAssetPrimaryAdaptor):
    domain: IAssetDomain

    def __init__(self, domain: IAssetDomain):
        self.domain = domain

    def create_asset(self, workspace_id:str, asset_creation: AssetCreation) -> Asset:
        """Create an asset from the given asset_creation object"""
        asset = self.domain.create_asset(workspace_id, asset_creation)
        return asset

    def get_asset(self, workspace_id:str, asset_id:str) -> Asset:
        """Get an asset from the given workspace_id and asset_id"""
        asset = self.domain.get_asset(workspace_id, asset_id)
        return asset

    def update_asset(self, workspace_id:str, asset_id:str, asset_update: AssetUpdate) -> Asset:
        asset = self.domain.update_asset(workspace_id, asset_id, asset_update)
        return asset

    def delete_asset(self, workspace_id:str, asset_id:str) -> dict:
        """Delete an asset from the given asset_id"""
        response = self.domain.delete_asset(workspace_id, asset_id)
        return response