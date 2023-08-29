import typer
from click import Context
from pydantic import BaseModel
from rich.console import Console
from typer.core import TyperGroup
from rich.panel import Panel
from typing_extensions import Annotated

from naas_python import logger
from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryInvoker,
    NaasRegistryError,
    Registry,
)


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


class TyperRegistryAdaptor(IRegistryInvoker):
    def __init__(self, domain: IRegistryDomain):
        self.domain = domain
        self.console = Console()

        self.app = typer.Typer(
            cls=OrderCommands,
            help="Naas Registry CLI",
            add_completion=False,
            no_args_is_help=True,
            pretty_exceptions_enable=False,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        @self.app.command()
        def create(
            name: str = typer.Option(
                ...,
                "--name",
                "-n",
                help="Registry name to be created, must be unique and comply with cloud provider naming rules",
            ),
        ):
            """Create a registry with the given name"""
            try:
                response = self.domain.create(name=name)
                print(response)
                self.console.print(Panel.fit(response.dict()))
            except NaasRegistryError as e:
                self.console.print(e.message, style="bold red")
            except Exception as e:
                logger.error(e)
                self.console.print("An error occurred", style="bold red")

        @self.app.command()
        def list():
            """List all registries for the current user"""
            try:
                response = self.domain.list()
                self.console.print(Panel.fit(response.dict()))
            except NaasRegistryError as e:
                self.console.print(e.message, style="bold red")
            except Exception as e:
                logger.error(e)
                self.console.print("An error occurred", style="bold red")

        @self.app.command()
        def get(
            name: str = typer.Option(
                ...,
                "--name",
                "-n",
                help="Registry name to be retrieved",
            ),
        ):
            """Get a registry with the given name"""
            try:
                response = self.domain.get_registry_by_name(name=name)
                self.console.print(Panel.fit(response.dict()))
            except NaasRegistryError as e:
                self.console.print(e.message, style="bold red")
            except Exception as e:
                logger.error(e)
                self.console.print("An error occurred", style="bold red")

        @self.app.command()
        def delete(
            name: str = typer.Option(
                ..., "--name", "-n", help="Registry name to be deleted"
            ),
        ):
            """Delete a registry with the given name"""
            try:
                response = self.domain.delete(name=name)
                self.console.print(Panel.fit(response.dict()))
            except NaasRegistryError as e:
                self.console.print(e.message, style="bold red")
            except Exception as e:
                logger.error(e)
                self.console.print("An error occurred", style="bold red")

        @self.app.command()
        def get_credentials(
            name: str = typer.Option(
                ..., "--name", "-n", help="Get access credentials for registry"
            ),
        ):
            """Get access credentials for registry"""
            try:
                response = self.domain.get_credentials(name=name)
                self.console.print(Panel.fit(response))
            except NaasRegistryError as e:
                self.console.print(e.message, style="bold red")
            except Exception as e:
                logger.error(e)
                self.console.print("An error occurred", style="bold red")
