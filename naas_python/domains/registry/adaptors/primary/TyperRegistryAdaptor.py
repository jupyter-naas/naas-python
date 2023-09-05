import typer
from click import Context
from pydantic import BaseModel
from rich.console import Console
from typer.core import TyperGroup
from rich.panel import Panel
from typing_extensions import Annotated

from logging import getLogger
from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryInvoker,
    RegistryDomainError,
    TyperRegistryError,
)

logger = getLogger(__name__)


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


class TyperRegistryAdaptor(IRegistryInvoker):
    def __init__(self, domain: IRegistryDomain):
        super().__init__()

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

        # Include all commands
        self.app.command()(self.list)
        self.app.command()(self.create)
        self.app.command()(self.get)
        self.app.command()(self.delete)
        self.app.command()(self.get_credentials)

    def create(
        self,
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
            self.console.print(Panel.fit(response.dict()))
        except RegistryDomainError as e:
            e.pretty_print()
        except Exception as e:
            return TyperRegistryError(e.args[0]).pretty_print()

    def list(
        self,
        page_size: int = typer.Option(0, help="Size of each page of results"),
        page_number: int = typer.Option(0, help="Target page number of results"),
    ):
        """List all registries for the current user"""
        try:
            response = self.domain.list(page_size=page_size, page_number=page_number)
            self.console.print(Panel.fit(response.dict()))
        except RegistryDomainError as e:
            e.pretty_print()
        except Exception as e:
            return TyperRegistryError(e.args[0]).pretty_print()

    def get(
        self,
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
        except RegistryDomainError as e:
            e.pretty_print()
        except Exception as e:
            return TyperRegistryError(e.args[0]).pretty_print()

    def delete(
        self,
        name: str = typer.Option(
            ..., "--name", "-n", help="Registry name to be deleted"
        ),
    ):
        """Delete a registry with the given name"""
        try:
            response = self.domain.delete(name=name)
            self.console.print(Panel.fit(response.dict()))
        except RegistryDomainError as e:
            e.pretty_print()
        except Exception as e:
            return TyperRegistryError(e.args[0]).pretty_print()

    def get_credentials(
        self,
        name: str = typer.Option(
            ..., "--name", "-n", help="Get access credentials for registry"
        ),
    ):
        """Get access credentials for registry"""
        try:
            response = self.domain.get_credentials(name=name)
            self.console.print(Panel.fit(response))
        except RegistryDomainError as e:
            e.pretty_print()
        except Exception as e:
            return TyperRegistryError(e.args[0]).pretty_print()
