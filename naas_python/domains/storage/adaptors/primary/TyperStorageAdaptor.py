from click import Context
from typer.core import TyperGroup

import typer
import os, json
from rich.console import Console
from logging import getLogger

from naas_python.utils.cicd import Pipeline

logger = getLogger(__name__)

from naas_python.domains.storage.StorageSchema import (
    Storage,
    IStorageInvoker,
    IStorageDomain 
)

class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)
    
class TyperStorageAdaptor(IStorageInvoker):
    def __init__(self, domain: IStorageDomain):
        super().__init__()    
    
        self.domain = domain
        self.console = Console()

        self.app = typer.Typer(
            cls=OrderCommands,
            help="Naas Storage CLI",
            add_completion=False,
            no_args_is_help=True,
            pretty_exceptions_enable=False,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        #TODO shorter "naas-python storage get-workspace-storage-object"
        #TODO missing descriptions
        self.app.command()(self.create_workspace_storage)
        self.app.command()(self.delete_workspace_storage)
        self.app.command()(self.list_workspace_storage_object)
        self.app.command()(self.list_workspace_storage)
        self.app.command()(self.post_workspace_storage_object)
        self.app.command()(self.get_workspace_storage_object)
        # self.app.command()(self.delete_workspace_storage_object)
        self.app.command()(self.create_workspace_storage_credentials)

    def create_workspace_storage(self,
        workspace_id: str = typer.Option(..., "--workspace", "-n", help="ID of the workspace"),
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            """Create a Workspace Storage"""
            storage = self.domain.create_workspace_storage(
                workspace_id=workspace_id,
                storage_name=storage_name,
            )

            if storage is None:
                print('Storage successfully created')
                
    def delete_workspace_storage(self,
        workspace_id: str = typer.Option(..., "--workspace", "-n", help="ID of the workspace"),
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            """Delete a Workspace Storage"""
            storage = self.domain.delete_workspace_storage(
                workspace_id=workspace_id,
                storage_name=storage_name,
            )

            if storage is None:
                print('Storage successfully deleted')                
        
    def list_workspace_storage(self,
        workspace_id: str = typer.Option(..., "--workspace", "-w", help="ID of the workspace"),        
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            """List Workspace Storage"""
            list_storage = self.domain.list_workspace_storage(
                workspace_id=workspace_id,
            )
            
            print("\nstorages",list_storage)
            
            # for object in list_storage["object"]:
            #     print(object)                
    
    #TODO better list                
    def list_workspace_storage_object(self,
        workspace_id: str = typer.Option(..., "--workspace", "-w", help="ID of the workspace"),
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),
        storage_prefix: str = typer.Option(..., "--prefix", "-p", help="Path prefix in the storage"),        
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            """List a Workspace Storage"""
            list_storage = self.domain.list_workspace_storage_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                storage_prefix=storage_prefix,
            )

            for object in list_storage["object"]:
                print(object)

    def post_workspace_storage_object(self,
        endpoint_url: str = typer.Option(..., "--endpoint", "-e", help="Endpoint of the workspace provided by credentials generation. \"s3://...\"."),        
        file_path = typer.Option(..., "--file", "-f", help="File to upload in the storage"),         
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
        if not os.path.isfile(file_path):
            print(f"File '{file_path}' does not exist.")
        else:   
                """Post a Workspace Storage Object"""
                post_workspace_storage_object = self.domain.post_workspace_storage_object(
                    endpoint_url=endpoint_url,
                    file_path=file_path
                )
                
    def get_workspace_storage_object(self,
        endpoint_url: str = typer.Option(..., "--endpoint", "-e", help="Endpoint of the workspace provided by credentials generation. \"s3://...\"."),
        storage_type: str = typer.Option("s3", "--storage-type", "-t", help="Type of the storage. Default \"s3\""),                                       
        storage_prefix: str = typer.Option(..., "--object", "-o", help="Path of the object in the storage. \"dir1/dir2/test.txt\""),        
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            if storage_prefix.endswith("/"):
                print("this is not an object")
            else:
                """Get a Workspace Storage Object"""
                get_workspace_storage_object = self.domain.get_workspace_storage_object(
                    endpoint_url=endpoint_url,
                    storage_prefix=storage_prefix,
                    storage_type=storage_type,
                )
                
                return get_workspace_storage_object

#TODO precise aws profile ?   
    def create_workspace_storage_credentials(self,
        workspace_id: str = typer.Option(..., "--workspace", "-n", help="ID of the workspace"),
        storage_type: str = typer.Option("s3", "--storage-type", help="Type of the storage. Default \"s3\""),        
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),        
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
        """Create Storage Credentials"""
        create_workspace_storage_credentials = self.domain.create_workspace_storage_credentials(
            workspace_id=workspace_id,
            storage_type=storage_type,
            storage_name=storage_name
        )
        #TODO better print
        print(create_workspace_storage_credentials)
        # print(json.dumps(    create_workspace_storage_credentials, indent=4))