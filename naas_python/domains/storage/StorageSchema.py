from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import List, Mapping, Any
from uuid import UUID

from naas_models.pydantic.storage_p2p import Storage
from .models.Storage import Storage, Object


# Secondary Adaptor
from naas_python.utils.exceptions import NaasException

logger = getLogger(__name__)

class IStorageAdaptor(metaclass=ABCMeta):
    @abstractmethod
    def create(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def list(self, 
        workspace_id: str, 
    ) -> dict:
        raise NotImplementedError
    
    @abstractmethod    
    def list_objects(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        storage_prefix: Object.__fields__['prefix'],        
    ) -> dict:
        raise NotImplementedError
    
    @abstractmethod    
    def delete_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        object_name: Object.__fields__['name'],   
    ) -> dict:
        raise NotImplementedError    
    
    @abstractmethod
    def create_credentials(self, workspace_id : str, storage_name: Storage.__fields__['name']) -> dict:
        raise NotImplementedError
    
class IStorageProviderAdaptor(metaclass=ABCMeta):

    provider_id : str

    @abstractmethod
    def post_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> bytes:
        raise NotImplementedError
    
    @abstractmethod
    def save_naas_credentials(self, workspace_id:str, storage_name:str, credentials:dict)-> str:
        raise NotImplementedError
    
# Domain
class IStorageDomain(metaclass=ABCMeta):
    adaptor: IStorageAdaptor
    storage_provider_adaptors : Mapping[str, IStorageProviderAdaptor]

    @abstractmethod    
    def create(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> dict:
        raise NotImplementedError

    @abstractmethod    
    def delete(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def list(self, 
        workspace_id: str, 
    ) -> dict:
        raise NotImplementedError
    
    @abstractmethod    
    def list_objects(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        storage_prefix: Object.__fields__['prefix'],        
    ) -> dict:
        raise NotImplementedError

    @abstractmethod    
    def delete_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        object_name: Object.__fields__['name'],
    ) -> dict:
        raise NotImplementedError     
    
    @abstractmethod
    def post_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def get_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,        
    ) -> bytes:
        raise NotImplementedError
   
    @abstractmethod    
    def create_credentials(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],        
    ) -> dict:
        raise NotImplementedError    
    
# Primary Adaptor
class IStorageInvoker(metaclass=ABCMeta):
    @abstractmethod
    def create(self, workspace_id: str, storage_name: Storage.__fields__['name']) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self,
        workspace_id: str, 
        storage_name: str = Storage.__fields__['name'],
    ) -> dict:
        raise NotImplementedError    
    
    @abstractmethod
    def list(self, workspace_id: str) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def create_credentials(self,                   
        workspace_id : str,
        storage_name = str,
    ) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def list_objects(self,        
        workspace_id: str, 
        storage_name: str, 
        storage_prefix: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def delete_object(self, 
        workspace_id: str, 
        storage_name: str,
        object_name: str) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def post_object(self,
        workspace_id: str, 
        storage_name: str,
        src_file: str,
        dst_file: str,
        ) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def get_object(self,
        workspace_id: str, 
        storage_name: str,
        src_file: str,
        dst_file: str,                   
    ) -> bytes:
        raise NotImplementedError
    
# Exceptions
class BadCredentials(NaasException):
    pass
class ClientError(NaasException):
    pass
class ConnectionError(NaasException):
    pass
class SSLError(NaasException):
    pass
class BotoCoreError(NaasException):
    pass
class StorageNotFoundError(NaasException):
    pass
class NoSuchBucket(NaasException):
    pass
class ExpiredToken(NaasException):
    pass
class FileNotFoundError(NaasException):
    pass
class BadRequest(NaasException):
    pass
class ForbiddenError(NaasException):
    pass
class APIError(NaasException):
    pass
class StorageProviderNotFound(NaasException):
    pass
class ServiceAuthenticationError(NaasException):
    pass
class ServiceStatusError(NaasException):
    pass
class ObjectAlreadyExists(NaasException):
    pass
