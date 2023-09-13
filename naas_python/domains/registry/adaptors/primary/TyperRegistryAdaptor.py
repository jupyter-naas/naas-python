from logging import getLogger
from typing import List

import rich
from rich.panel import Panel

import typer
from click import Context
from rich.console import Console
from rich.table import Table
from typer.core import TyperGroup

from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryInvoker,
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

    def _list_preview(self, data: List[dict], headers: list):
        if not isinstance(data, list):
            raise TypeError("Data must be a list of dicts, not {}".format(type(data)))

        # Determine column widths based on the longest values
        column_widths = [max(len(str(item)) for item in col) for col in zip(*data)]

        # Print the headers
        header_format = "  ".join(
            f"{header:<{width}}" for header, width in zip(headers, column_widths)
        )
        print(header_format)

        # Print the data
        for row in data:
            row_format = "  ".join(
                f"{str(item):<{width}}" for item, width in zip(row, column_widths)
            )
            print(row_format)

    def create(
        self,
        name: str = typer.Option(
            ...,
            "--name",
            "-n",
            help="Registry name to be created, must be unique and comply with cloud provider naming rules",
        ),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Preview the response in the terminal using rich",
        ),
    ):
        """Create a registry with the given name"""
        registry = self.domain.create(name=name)

        # Extract the data
        data = [registry.registry.dict().values()]

        # Define column headers using the determined widths
        headers = [key.upper() for key in registry.registry.dict().keys()]

        if rich_preview:
            # Create a Rich Table
            table = Table(show_header=True, header_style="bold")
            # Add columns to the table
            for header in headers:
                table.add_column(header, justify="center")

            # Add data rows to the table
            for row in data:
                table.add_row(*row)

            # Print the table
            rich.print(table)

        else:
            self._list_preview(data, headers)

    def list(
        self,
        page_size: int = typer.Option(0, help="Size of each page of results"),
        page_number: int = typer.Option(0, help="Target page number of results"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Preview the response in the terminal using rich",
        ),
    ):
        """List all registries for the current user"""
        registry_list = self.domain.list(page_size=page_size, page_number=page_number)

        # Extract the data
        data = [registry.dict().values() for registry in registry_list.registries]

        if len(data) == 0:
            print("No matching results found.")
            return

        # Define column headers using the determined widths
        headers = [key.upper() for key in registry_list.registries[0].dict().keys()]

        if rich_preview:
            # Create a Rich Table
            table = Table(show_header=True, header_style="bold")
            # Add columns to the table
            for header in headers:
                table.add_column(header, justify="center")

            # Add data rows to the table
            for row in data:
                table.add_row(*row)

            # Print the table
            rich.print(table)

        else:
            self._list_preview(data, headers)

    def get(
        self,
        name: str = typer.Option(
            ...,
            "--name",
            "-n",
            help="Registry name to be retrieved",
        ),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Preview the response in the terminal using rich",
        ),
    ):
        """Get a registry with the given name"""
        registry = self.domain.get_registry_by_name(name=name)

        # Extract the data
        data = [registry.registry.dict().values()]

        # Define column headers using the determined widths
        headers = [key.upper() for key in registry.registry.dict().keys()]

        if rich_preview:
            # Create a Rich Table
            table = Table(show_header=True, header_style="bold")
            # Add columns to the table
            for header in headers:
                table.add_column(header, justify="center")

            # Add data rows to the table
            for row in data:
                table.add_row(*row)

            # Print the table
            rich.print(table)

        else:
            self._list_preview(data, headers)

    def delete(
        self,
        name: str = typer.Option(
            ..., "--name", "-n", help="Registry name to be deleted"
        ),
    ):
        """Delete a registry with the given name"""
        self.domain.delete(name=name)

    def get_credentials(
        self,
        name: str = typer.Option(
            ..., "--name", "-n", help="Get access credentials for registry"
        ),
    ):
        """Get access credentials for registry"""
        response = self.domain.get_credentials(name=name)

        with open(f"{name}-credentials.txt", "w") as f:
            f.write(response.json())

        self.console.print(
            Panel.fit(f"Registry credentials saved to '{name}-credentials.txt'")
        )
