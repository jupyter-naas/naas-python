import typer
from typer.core import TyperGroup
from click import Context
from rich.console import Console
from rich import print
from logging import getLogger

from naas_python.domains.asset.AssetSchema import (
    IAssetDomain,
    IAssetPrimaryAdaptor,
    # IAssetInvoker,
    Asset,
    AssetCreation,
    AssetUpdate
)

logger = getLogger(__name__)

class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)
    
class TyperAssetAdaptor(IAssetPrimaryAdaptor):
    def __init__(self, domain: IAssetDomain):
        super().__init__()

        self.domain = domain
        self.console = Console()

        self.app = typer.Typer(
            cls=OrderCommands,
            help="Naas Asset CLI",
            add_completion=False,
            no_args_is_help=True,
            pretty_exceptions_enable=False,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        self.app.command("create-asset")(self.create_asset)
        self.app.command("delete-asset")(self.delete_asset)
        self.app.command("get-asset")(self.get_asset)
        self.app.command("update-asset")(self.update_asset)

    def create_asset(self, 
        workspace_id:str = typer.Option(None, "--workspace-id", "-w", help="ID of the workspace"),
        # asset_creation: AssetCreation = typer.Option(..., "--object", "-o", help="Storage object to create an asset from."),
        storage: str = typer.Option(None, "--storage", "-s", help="Storage name to create an asset from. ie:\"data1\""),
        object: str = typer.Option(None, "--object", "-o", help="Object to create an asset from. ie:\"/dir1/tmp.txt\""),
        version: str = typer.Option(None, "--object-version", "-ov", help="Optional version of the storage object"),
        visibility: str = typer.Option(None, "--visibility", "-vis", help="Optional visibility of the asset"),
        content_disposition: str = typer.Option(None, "--content-disposition", "-cd", help="Optinal content disposition of the asset"),
        password: str = typer.Option(None, "--password", "-p", help="Optional password to decrypt the storage object"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        ))-> Asset:
            asset_creation_args:dict = {"asset_creation": {}}
            if workspace_id is not None: 
                asset_creation_args["asset_creation"]["workspace_id"] = workspace_id
            if storage is not None and object is not None:
                asset_creation_args["asset_creation"]["storage_name"] = storage
                asset_creation_args["asset_creation"]["object_name"] = object                
            if version is not None:
                asset_creation_args["asset_creation"]["object_version"] = version
            if visibility is not None:
                asset_creation_args["asset_creation"]["visibility"] = visibility
            if content_disposition is not None:
                asset_creation_args["asset_creation"]["content_disposition"] = content_disposition
            if password is not None:
                asset_creation_args["asset_creation"]["password"] = password
            
            asset_creation : AssetCreation = asset_creation_args
            print("creating asset...")
            asset = self.domain.create_asset(workspace_id, asset_creation)

    def get_asset(self, 
        workspace_id:str = typer.Option(None, "--workspace-id", "-w", help="ID of the workspace"),
        asset_id: str = typer.Option(None, "--asset-id", "-id", help="ID of the asset to get."),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        ))-> Asset:
            print("getting asset...")
            asset = self.domain.get_asset(workspace_id, asset_id)
            print(asset)

    def update_asset(self,
        workspace_id:str = typer.Option(None, "--workspace-id", "-w", help="ID of the workspace"),
        asset_id: str = typer.Option(None, "--asset-id", "-id", help="ID of the asset to update."),
        visibility: str = typer.Option(None, "--visibility", "-vis", help="Optional visibility of the asset"),
        content_disposition: str = typer.Option(None, "--content-disposition", "-cd", help="Optinal content disposition of the asset"),
        # password: str = typer.Option(None, "--password", "-p", help="Optional password to decrypt the storage object"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
        ))-> Asset:
            
            asset_update_args:dict = {"asset_update": {}}
            if visibility is not None:
                asset_update_args["asset_update"]["visibility"] = visibility
            if content_disposition is not None:
                asset_update_args["asset_update"]["content_disposition"] = content_disposition
            #TODO feature                
            # if password is not None:
            #     asset_update_args["asset_update"]["password"] = password
            asset_update : AssetUpdate = asset_update_args
            print("updating asset...")
            asset = self.domain.update_asset(workspace_id, asset_id, asset_update)
            print(asset)

    def delete_asset(self, 
        workspace_id:str = typer.Option(..., "--workspace-id", "-w", help="ID of the workspace"),
        asset_id: str = typer.Option(..., "--asset-id", "-id", help="ID of the asset to delete."),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the information as a table",
    ))-> None:
        print("deleting asset...")
        self.domain.delete_asset(workspace_id, asset_id)
        print("Done.")