import json
import os
import time
from logging import getLogger
from typing import List
from uuid import UUID

import rich
import typer
from click import Context
from pydantic import BaseModel
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from typer.core import TyperGroup
from typing_extensions import Annotated

from naas_python.domains.secret.adaptors.primary.utils import PydanticTableModel
from naas_python.domains.secret.SecretSchema import (
    ISecretDomain,
    ISecretInvoker,
    SecretConflictError,
)
# from naas_python.domains.secret.SecretSchema import SecrettryConflictError
from naas_python.utils.cicd import Pipeline

logger = getLogger(__name__)


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


class TyperSecretAdaptor(ISecretInvoker):
    def __init__(self, domain: ISecretDomain):
        super().__init__()

        self.domain = domain
        self.console = Console()

        self.app = typer.Typer(
            cls=OrderCommands,
            help="Naas Secret CLI",
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
        name: str = typer.Option(..., "--name", "-n", help="Name of the secret"),
        value: str = typer.Option(..., "--value", "-v", help="Value of the secret"),

        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the Secret information as a table",
        ),
    ):
        """Create a Secret with the given specifications"""
        secret = self.domain.create(
            name=name,
            value=value
        )

        if secret is None:
            print('Secret Successfully created')

    def get(
        self,
        name: str = typer.Option(..., "--name", "-n", help="Name of the secret"),
        rich_preview: bool = typer.Option(
            os.environ.get("NAAS_CLI_RICH_PREVIEW", False),
            "--rich-preview",
            "-rp",
            help="Rich preview of the secret information as a table",
        ),
    ):
        """Get a secret with the given name"""
        secret = self.domain.get(name=name)
        
        if rich_preview:
            self.console.print(PydanticTableModel([secret]).table)

        else:
            print(secret.value)

    def delete(
        self,
        name: str = typer.Option(..., "--name", "-n", help="Name of the secret"),
    ):
        self.domain.delete(name=name)

        print(f"Secret '{name}' deleted successfully")

    def list(
        self,
        page_size: int = typer.Option(0, help="Size of each page of results"),
        page_number: int = typer.Option(0, help="Target page number of results"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the secret information as a table",
        ),
    ):
        """List all secrets for the current user"""
        secret_list = self.domain.list(page_size=page_size, page_number=page_number)

        data = []
        headers = []

        # Extract the data and headers
        for secret in secret_list:
            _secret_dict = secret.dict()


            data.append(list(_secret_dict.values()))  # Append a list of values to data

            headers = [key.upper() for key in _secret_dict.keys()]

        if len(data) == 0:
            print("No matching results found.")
            return

        headers = [key.upper() for key in _secret_dict.keys()]

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
