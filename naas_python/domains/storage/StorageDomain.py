from naas_python.domains.storage.models.Storage import Storage

from typing import List, Mapping

from naas_python.domains.storage.StorageSchema import (
    IStorageDomain,
    IStorageAdaptor,
    IStorageProviderAdaptor,
    Storage,
    Object,
    StorageProviderNotFound
)
class StorageDomain(IStorageDomain):
    def __init__(self, adaptor: IStorageAdaptor,
        storage_provider_adaptors : Mapping[str, IStorageProviderAdaptor]
        ) : 
        
        self.adaptor = adaptor
        self.storage_provider_adaptors : Mapping[str, IStorageProviderAdaptor] = storage_provider_adaptors

############### API ###############
    def create(self, 
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
    ) -> dict:
        response = self.adaptor.create(
            workspace_id=workspace_id, 
            storage_name=storage_name,
        )
        return response

    def delete(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name']
    ) -> dict:
        response = self.adaptor.delete(
            workspace_id=workspace_id,
            storage_name=storage_name,
        )
        return response
    
    def list(self, 
        workspace_id: str, 
    ) -> dict:
        response = self.adaptor.list(
            workspace_id=workspace_id,
        )
        return response     
    
    def list_objects(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name'],
        storage_prefix: Object.__fields__['prefix'],
    ) -> dict:
        response = self.adaptor.list_objects(
            workspace_id=workspace_id,
            storage_name=storage_name,
            storage_prefix=storage_prefix,
        )
        return response
    
    def delete_object(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name'],
        object_name: Storage.__fields__['name'],
    ) -> dict:
        response = self.adaptor.delete_object(
            workspace_id=workspace_id,
            storage_name=storage_name,
            object_name=object_name,
        )
        return response    

    def create_credentials(self,         
        workspace_id: str,
        storage_name: Storage.__fields__['name'],        
    ) -> dict:
        credentials = self.adaptor.create_credentials(workspace_id, storage_name)
        storage_provider_adaptor = self.__get_storage_provider_adaptor(workspace_id=workspace_id, storage_name=storage_name)
        storage_provider_adaptor.save_naas_credentials(workspace_id, storage_name, credentials)
        return credentials

############### BOTO ###############
    def __get_storage_provider(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name']
    ) -> str:
        #TODO This function should check in ~.naas/credentials to grab the provider id (s3;azure;gcp;...)
        return 's3'

    def __get_storage_provider_adaptor(self,
                                       workspace_id: str,
                                       storage_name: Storage.__fields__['name']
                                       ) -> IStorageProviderAdaptor:
        storage_provider_id = self.__get_storage_provider(workspace_id, storage_name)
        if storage_provider_id not in self.storage_provider_adaptors:
            raise StorageProviderNotFound(f'Provider "{storage_provider_id}" is not implemented or not loaded.')
        return self.storage_provider_adaptors[storage_provider_id]


    def post_object(self, 
        workspace_id: str,
        storage_name: str,
        src_file: str,
        dst_file: str,  
    ) -> dict:

        storage_provider_id = self.__get_storage_provider(workspace_id, storage_name)

        if storage_provider_id not in self.storage_provider_adaptors:
            raise StorageProviderNotFound(f'Provider "{storage_provider_id}" is not implemented or not loaded.')
        
        storage_provider_adaptor : IStorageProviderAdaptor = self.storage_provider_adaptors[storage_provider_id]

        if not storage_provider_adaptor.valid_naas_credentials(workspace_id, storage_name):
            credentials = self.adaptor.create_credentials(workspace_id, storage_name)
            storage_provider_adaptor.save_naas_credentials(workspace_id, storage_name, credentials)

        response = storage_provider_adaptor.post_object(workspace_id=workspace_id, storage_name=storage_name, src_file=src_file, dst_file=dst_file)
        return response
    
    def get_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> bytes:

        storage_provider_id = self.__get_storage_provider(workspace_id, storage_name)

        if storage_provider_id not in self.storage_provider_adaptors:
            raise StorageProviderNotFound(f'Provider "{storage_provider_id}" is not implemented or not loaded.')
        
        storage_provider_adaptor : IStorageProviderAdaptor = self.storage_provider_adaptors[storage_provider_id]

        if not storage_provider_adaptor.valid_naas_credentials(workspace_id, storage_name):
            credentials = self.adaptor.create_credentials(workspace_id, storage_name)
            storage_provider_adaptor.save_naas_credentials(workspace_id, storage_name, credentials)

        response = storage_provider_adaptor.get_object(workspace_id=workspace_id, storage_name=storage_name, src_file=src_file, dst_file=dst_file)
        return response
