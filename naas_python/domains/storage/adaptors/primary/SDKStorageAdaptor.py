import os

from naas_python.domains.storage.StorageSchema import (
    IStorageDomain,
    IStorageInvoker,
)

class SDKStorageAdaptor(IStorageInvoker):
    domain: IStorageDomain

    def __init__(self, domain: IStorageDomain):
        self.domain = domain

############### API ############### 
# Workspace Storage
    def create_workspace_storage(self, workspace_id: str = "", storage_name: str = "") -> None:
        response = self.domain.create_workspace_storage(
            workspace_id=workspace_id,
            storage_name=storage_name,
        )
        return response
    
    def delete_workspace_storage(self, workspace_id: str = "", storage_name: str = "") -> None:
        response = self.domain.delete_workspace_storage(
                workspace_id=workspace_id,
                storage_name=storage_name,
            )
        return response
    
    def list_workspace_storage(self, workspace_id: str = "") -> str:
        response = self.domain.list_workspace_storage(
                workspace_id=workspace_id,
            )
        return response
    
    def create_workspace_storage_credentials(self, workspace_id: str = "", storage_name: str = ""):
        response = self.domain.create_workspace_storage_credentials(
                workspace_id=workspace_id,
                storage_name=storage_name,
            )
        return response  

# Workspace Storage Object
    def list_workspace_storage_object(self, 
        workspace_id: str = "", 
        storage_name: str = "", 
        storage_prefix: str = "") -> str:

        response = self.domain.list_workspace_storage_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                storage_prefix=storage_prefix,
            )
        return response
    
    def delete_workspace_storage_object(self, 
        workspace_id: str = "", 
        storage_name: str = "",
        object_name: str = "",
        ) -> None:

        response = self.domain.delete_workspace_storage_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                object_name=object_name,
            )
        return response    

############### BOTO3 ###############
    def post_workspace_storage_object(self,
        workspace_id: str = "", 
        storage_name: str = "",
        src_file: str = "",
        dst_file: str = "",
    ) -> bytes:
        if os.path.isfile(src_file):
            response = self.domain.post_workspace_storage_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                src_file=src_file,
                dst_file=dst_file,
            )
            return response            
        else:
            raise FileNotFoundError(f"File not found: {src_file}")

    def get_workspace_storage_object(self, 
        workspace_id: str = "", 
        storage_name: str = "",
        src_file: str = "",
        dst_file: str = "",
        ) -> bytes:

        response = self.domain.get_workspace_storage_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                src_file=src_file,
                dst_file=dst_file,
            )
        return response
