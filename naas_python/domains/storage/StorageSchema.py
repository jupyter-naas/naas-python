from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import List

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
        raise NotImplementedError
    
    @abstractmethod    
    def list_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        storage_prefix: Object.__fields__['prefix'],        
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod    
    def delete_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        object_name: Object.__fields__['name'],   
    ) -> None:
        raise NotImplementedError    
    
class IStorageProviderAdaptor(metaclass=ABCMeta):

    provider_id : str

    @abstractmethod
    def post_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> bytes:
        raise NotImplementedError
    
# Domain
class IStorageDomain(metaclass=ABCMeta):
    adaptor: IStorageAdaptor
    storage_provider_adaptors : List[IStorageProviderAdaptor]
    # storage_provider_adaptors : Map[str, IStorageProviderAdaptor]
    #TODO to be validated

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
        raise NotImplementedError
    
    @abstractmethod    
    def list_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        storage_prefix: Object.__fields__['prefix'],        
    ) -> None:
        raise NotImplementedError

    @abstractmethod    
    def delete_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        object_name: Object.__fields__['name'],
    ) -> None:
        raise NotImplementedError     
    
    @abstractmethod
    def post_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def get_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,        
    ) -> bytes:
        raise NotImplementedError
   
    
    @abstractmethod    
    def create_workspace_storage_credentials(self,
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
    def delete_workspace_storage_object(self, **kwargs):
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