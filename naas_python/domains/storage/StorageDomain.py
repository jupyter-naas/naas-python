from .models.Storage import Storage

from naas_python.domains.storage.StorageSchema import (
    IStorageDomain,
    IStorageAdaptor,
    Storage,
    Object,
)

#TODO fix None return
class StorageDomain(IStorageDomain):
    def __init__(self, adaptor: IStorageAdaptor):
        self.adaptor = adaptor

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
    
    def post_workspace_storage_object(self, 
        endpoint_url: str,
        file_path: str,    
    ) -> None:
        response = self.adaptor.post_workspace_storage_object(
            endpoint_url=endpoint_url,
            file_path=file_path
        )
        return response
    
    def get_workspace_storage_object(self,
        endpoint_url: str,
        storage_prefix: Object.__fields__['prefix'],
        storage_type: str,
    ) -> bytes:
        response = self.adaptor.get_workspace_storage_object(
            endpoint_url=endpoint_url,
            storage_prefix=storage_prefix,
            storage_type=storage_type,
        )
        return response
    
    def create_workspace_storage_credentials(self,         
        workspace_id: str,
        storage_type: str,
        storage_name: Storage.__fields__['name'],        
    ) -> None:
        response = self.adaptor.create_workspace_storage_credentials(
            workspace_id=workspace_id,
            storage_type=storage_type,            
            storage_name=storage_name
        )
        return response