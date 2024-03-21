from abc import ABCMeta, abstractmethod
from logging import getLogger

from naas_models.pydantic.storage_p2p import *
from .models.Storage import Storage, Object


# Secondary Adaptor

from naas_python.utils.exceptions import NaasException

logger = getLogger(__name__)

class IStorageAdaptor(metaclass=ABCMeta):
    @abstractmethod    
    def create_workspace_storage(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def delete_workspace_storage(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def list_workspace_storage(self, 
        workspace_id: str, 
    ) -> None:
        response = self.adaptor.list_workspace_storage(
            workspace_id=workspace_id,
        )
        return response
    
    @abstractmethod    
    def list_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        storage_prefix: Object.__fields__['prefix'],        
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def post_workspace_storage_object(self, 
        endpoint_url: str,
        file_path: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_workspace_storage_object(self,
        endpoint_url: str,
        storage_prefix: Object.__fields__['prefix'],
        storage_type: str 
    ) -> bytes:
        raise NotImplementedError 

    @abstractmethod    
    def create_workspace_storage_credentials(self,
        storage_type: str,                                     
        workspace_id: str,
        storage_name: Storage.__fields__['name'],        
    ) -> None:
        raise NotImplementedError     
        
# Domain

class IStorageDomain(metaclass=ABCMeta):
    adaptor: IStorageAdaptor
    
    @abstractmethod    
    def create_workspace_storage(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> None:
        raise NotImplementedError

    @abstractmethod    
    def delete_workspace_storage(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def list_workspace_storage(self, 
        workspace_id: str, 
    ) -> None:
        response = self.adaptor.list_workspace_storage(
            workspace_id=workspace_id,
        )
        return response    
    
    @abstractmethod    
    def list_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        storage_prefix: Object.__fields__['prefix'],        
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def post_workspace_storage_object(self,
        endpoint_url: str,                                       
        file_path: str     
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def get_workspace_storage_object(self,
        endpoint_url: str,
        storage_prefix: Object.__fields__['prefix'],
        storage_type: str, 
    ) -> bytes:
        raise NotImplementedError     
    
    @abstractmethod    
    def create_workspace_storage_credentials(self,
        storage_type: str,                                     
        workspace_id: str,
        storage_name: Storage.__fields__['name'],        
    ) -> None:
        raise NotImplementedError    
    
# Primary Adaptor

class IStorageInvoker(metaclass=ABCMeta):
    @abstractmethod
    def create_workspace_storage(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete_workspace_storage(self, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def list_workspace_storage(self, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def list_workspace_storage_object(self, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def post_workspace_storage_object(self, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    def get_workspace_storage_object(self, **kwargs):
        raise NotImplementedError     
    
    @abstractmethod
    def create_workspace_storage_credentials(self, **kwargs):
        raise NotImplementedError       