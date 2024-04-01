from .models.Storage import Storage

from typing import List

from naas_python.domains.storage.StorageSchema import (
    IStorageDomain,
    IStorageAdaptor,
    IStorageProviderAdaptor,
    Storage,
    Object,
    StorageProviderNotFound
)
class StorageDomain(IStorageDomain):
    def __init__(self, adaptor: IStorageAdaptor, storage_provider_adaptors : List[IStorageProviderAdaptor]):
        # List[IStorageProviderAdaptor])
        #Map[str : IStorageProviderAdaptor])
        self.adaptor = adaptor
        self.storage_provider_adaptors = storage_provider_adaptors

############### API ###############
    def create_workspace_storage(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name'],
    ) -> None:
        response = self.adaptor.create_workspace_storage(
            workspace_id=workspace_id, 
            storage_name=storage_name,
        )
        return response

    def delete_workspace_storage(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name']
    ) -> None:
        response = self.adaptor.delete_workspace_storage(
            workspace_id=workspace_id,
            storage_name=storage_name,
        )
        return response
    
    def list_workspace_storage(self, 
        workspace_id: str, 
    ) -> None:
        response = self.adaptor.list_workspace_storage(
            workspace_id=workspace_id,
        )
        return response     
    
    def list_workspace_storage_object(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name'],
        storage_prefix: Object.__fields__['prefix'],
    ) -> None:
        response = self.adaptor.list_workspace_storage_object(
            workspace_id=workspace_id,
            storage_name=storage_name,
            storage_prefix=storage_prefix,
        )
        return response

    def create_workspace_storage_credentials(self,         
        workspace_id: str,
        storage_name: Storage.__fields__['name'],        
    ) -> None:
        response = self.adaptor.generate_credentials(
            workspace_id=workspace_id,           
            storage_name=storage_name
        )
        return response  

    #TODO
    def __get_storage_provider(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name']
    ) -> str:
        # This function should check in ~.naas/credentials to grab the provider id (s3;azure;gcp;...)
        return 's3'


    def post_workspace_storage_object(self, 
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,  
    ) -> None:

        storage_provider_id = self.__get_storage_provider(workspace_id, storage_name)

        if storage_provider_id not in self.storage_provider_adaptors:
            raise StorageProviderNotFound(f'Provider "{storage_provider_id}" is not implemented or not loaded.')
        
        storage_provider : IStorageProviderAdaptor = self.storage_provider_adaptors[storage_provider_id]

        response = storage_provider.post_workspace_storage_object(workspace_id=workspace_id, storage_name=storage_name, src_file=src_file, dst_file=dst_file)
        return response
    
    def get_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> bytes:

        storage_provider_id = self.__get_storage_provider(workspace_id, storage_name)

        if storage_provider_id not in self.storage_provider_adaptors:
            raise StorageProviderNotFound(f'Provider "{storage_provider_id}" is not implemented or not loaded.')
        
        storage_provider : IStorageProviderAdaptor = self.storage_provider_adaptors[storage_provider_id]

        response = storage_provider.get_workspace_storage_object(workspace_id=workspace_id, storage_name=storage_name, src_file=src_file, dst_file=dst_file)
        return response

    def delete_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        object_name: Object.__fields__['name'],
    ) -> None:
        
        storage_provider_id = self.__get_storage_provider(workspace_id, storage_name)

        if storage_provider_id not in self.storage_provider_adaptors:
            raise StorageProviderNotFound(f'Provider "{storage_provider_id}" is not implemented or not loaded.')
        
        storage_provider : IStorageProviderAdaptor = self.storage_provider_adaptors[storage_provider_id]

        response = storage_provider.delete_workspace_storage_object(workspace_id=workspace_id, storage_name=storage_name, object_name=object_name)
        return response