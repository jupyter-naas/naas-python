from click import Context
from typer.core import TyperGroup

import typer
import os, json
from rich.console import Console
from rich.table import Table
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

        self.app.command("create")(self.create_workspace_storage)
        self.app.command("delete")(self.delete_workspace_storage)
        self.app.command("list")(self.list_workspace_storage)
        self.app.command("list-object")(self.list_workspace_storage_object)
        self.app.command("put-object")(self.post_workspace_storage_object)
        self.app.command("get-object")(self.get_workspace_storage_object)
        self.app.command("delete-object")(self.delete_workspace_storage_object)
        self.app.command("connect")(self.create_workspace_storage_credentials)

############### API ###############
    def create_workspace_storage(self,
        workspace_id: str = typer.Option(..., "--workspace", "-w", help="ID of the workspace"),
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            """Create a Workspace Storage"""
            print("creating storage...")
            storage = self.domain.create_workspace_storage(
                workspace_id=workspace_id,
                storage_name=storage_name,
            )
            print(f"Storage {storage_name} created.")
    
    def delete_workspace_storage(self,
        workspace_id: str = typer.Option(..., "--workspace", "-w", help="ID of the workspace"),
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            """Delete a Workspace Storage"""
            print("deleting storage...")
            storage = self.domain.delete_workspace_storage(
                workspace_id=workspace_id,
                storage_name=storage_name,
            )
            print(f"Storage {storage_name} deleted.")

    def list_workspace_storage(self,
        workspace_id: str = typer.Option(..., "--workspace", "-w", help="ID of the workspace"),        
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            """List Workspace Storages"""
            list_storage = self.domain.list_workspace_storage(
                workspace_id=workspace_id,
            )
            if rich_preview:
                console = Console()
                table = Table(show_header=True, header_style="bold black")
                table.add_column("Name")

                for storage in list_storage['storage']:
                    table.add_row(storage['name'])

                console.print(table)
            else:
                print(list_storage)
         
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
            """List a Workspace Storage Objects"""
            list_storage_object = self.domain.list_workspace_storage_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                storage_prefix=storage_prefix,
            )
            if rich_preview:
                console = Console()
                table = Table(show_header=True, header_style="bold black")
                table.add_column("Name")
                table.add_column("Type")
                table.add_column("Prefix")
                table.add_column("Size")
                table.add_column("Last Modified")

                for object in list_storage_object["object"]:
                    table.add_row(object['name'], object['type'], object['prefix'], object['size'], object['lastmodified'])

                console.print(table)
            else:
                print(list_storage_object)

    def delete_workspace_storage_object(self,                                             
        workspace_id: str = typer.Option(..., "--workspace", "-w", help="ID of the workspace"),
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),                                      
        object_name: str = typer.Option(..., "--object", "-o", help="Name of Object or Folder to remove."),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
        """Delete a Workspace Storage Object"""
        print("Deleting object...")
        response = self.domain.delete_workspace_storage_object(
            workspace_id=workspace_id,
            storage_name=storage_name,
            object_name=object_name,
        )
        print("Object deleted.")
                
    def create_workspace_storage_credentials(self,
        workspace_id: str = typer.Option(..., "--workspace", "-w", help="ID of the workspace"),
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),        
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
        """Create Storage Credentials"""
        print("Creating credentials...")
        response = self.domain.create_workspace_storage_credentials(
            workspace_id=workspace_id,
            storage_name=storage_name
        )
        print("Credentials created.")                

############### BOTO3 ###############
    def post_workspace_storage_object(self,
        workspace_id: str = typer.Option(..., "--workspace", "-w", help="ID of  the workspace"),
        storage_name: str = typer.Option(..., "--storage", "-s", help="Name of the storage"),      
        src_file: str = typer.Option(..., "--source", "-src", help="File path to upload in the storage"),
        dst_file: str = typer.Option(..., "--destination", "-dst", help="Destination file path in the storage"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ) -> None:
        """Post a Workspace Storage Object"""        
        if not os.path.isfile(src_file):
            print(f"File '{src_file}' does not exist.")
        else:
            print("Uploading object...")
            response = self.domain.post_workspace_storage_object(
                workspace_id=workspace_id,
                storage_name=storage_name,
                src_file=src_file,
                dst_file=dst_file
            )
            print("Object uploaded.")

    def get_workspace_storage_object(self,
        workspace_id: str = typer.Option(None, "--workspace", "-w", help="ID of the workspace"),
        storage_name: str = typer.Option(None, "--storage", "-s", help="Name of the storage"),
        src_file: str = typer.Option(None, "--source", "-src", help="File path to download in the storage"),                               
        dst_file: str = typer.Option(None, "--destination", "-dst", help="Destination file path in the filesystem"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        )
    ):
            """Get a Workspace Storage Object"""            
            if src_file.endswith("/"):
                print("this is not an object")
            else :
                print("Downloading object...")
                response = self.domain.get_workspace_storage_object(
                    workspace_id=workspace_id,
                    storage_name=storage_name,
                    src_file=src_file,
                    dst_file=dst_file
                )
                print("Object downloaded.")
