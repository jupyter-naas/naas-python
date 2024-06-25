from abc import ABCMeta, abstractmethod

from naas_models.pydantic.asset_p2p import *
from .models.Asset import Asset, AssetCreation, AssetUpdate

from naas_python.utils.exceptions import NaasException

# Exception
class AssetNotFound(NaasException): pass
class AssetConflictError(NaasException): pass
class AssetRequestError(NaasException): pass

# Secondary adaptor
class IAssetAdaptor(metaclass=ABCMeta):
    
    @abstractmethod
    def create_asset(self, workspace_id:str, asset_creation:AssetCreation) -> Asset:
        raise NotImplementedError()
    
    @abstractmethod
    def get_asset(self, workspace_id:str, asset_id:str) -> Asset:
        raise NotImplementedError()  

    @abstractmethod
    def update_asset(self, workspace_id:str, asset_id:str, asset_update: AssetUpdate) -> Asset:
        raise NotImplementedError()
    
    @abstractmethod
    def delete_asset(self, workspace_id:str, asset_id:str) -> None:
        raise NotImplementedError()

# Domain
class IAssetDomain(metaclass=ABCMeta):
    adaptor: IAssetAdaptor

    @abstractmethod
    def create(self, workspace_id:str, asset_creation:AssetCreation) -> Asset:
        raise NotImplementedError()
    
    @abstractmethod
    def get(self, workspace_id:str, asset_id:str) -> Asset:
        raise NotImplementedError()

    @abstractmethod
    def update(self, workspace_id:str, asset_id:str, asset_update: AssetUpdate) -> Asset:
        raise NotImplementedError()    
    
    @abstractmethod
    def delete(self, workspace_id:str, asset_id:str) -> None:
        raise NotImplementedError()

# Primary Adaptor
class IAssetPrimaryAdaptor:
    pass
