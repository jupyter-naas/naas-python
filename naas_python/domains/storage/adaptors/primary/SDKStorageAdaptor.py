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
    def create(self, workspace_id: str = "", storage_name: str = "") -> dict:
        response = self.domain.create(
            workspace_id=workspace_id,
            storage_name=storage_name,
        )
        return response

    def delete(self, workspace_id: str = "", storage_name: str = "") -> None:
        response = self.domain.delete(
                workspace_id=workspace_id,
                storage_name=storage_name,
    )
    
    def list(self, workspace_id: str = "") -> dict:
        response = self.domain.list(
                workspace_id=workspace_id,
            )
        return response
    
    def create_credentials(self, workspace_id: str = "", storage_name: str = ""):
        response = self.domain.create_credentials(
                workspace_id=workspace_id,
                storage_name=storage_name,
        )
        return response

# Workspace Storage Object
    def list_objects(self, 
        workspace_id: str = "", 
        storage_name: str = "", 
        storage_prefix: str = "") -> dict:

        response = self.domain.list_objects(
                workspace_id=workspace_id,
                storage_name=storage_name,
                storage_prefix=storage_prefix,
            )
        return response
    
    def delete_object(self, 
        workspace_id: str = "", 
        storage_name: str = "",
        object_name: str = "",
        ) -> None:

        response = self.domain.delete_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                object_name=object_name,
            )
                
############### BOTO3 ###############
    def post_object(self,
        workspace_id: str = "", 
        storage_name: str = "",
        src_file: str = "",
        dst_file: str = "",
    ) -> dict:
        if os.path.isfile(src_file):
            response = self.domain.post_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                src_file=src_file,
                dst_file=dst_file,
            )
            return response         
        else:
            raise FileNotFoundError(f"File not found: {src_file}")

    def get_object(self, 
        workspace_id: str = "", 
        storage_name: str = "",
        src_file: str = "",
        dst_file: str = "",
    ) -> bytes:

        response = self.domain.get_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                src_file=src_file,
                dst_file=dst_file,
        )
        return response
