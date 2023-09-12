import json
import os
from logging import getLogger
from typing import List

import rich
import typer
from click import Context
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from typer.core import TyperGroup
from typing_extensions import Annotated

from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceInvoker,
    Space,
)

logger = getLogger(__name__)


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


class PydanticTableModel:
    def __init__(self, models: List[BaseModel]):
        super().__init__()
        self.models = models
        self.rich_table()

    def rich_table(self):
        # Get the field names from the first model in the list, and remove the resources and protocols fields
        field_names = [
            field
            for field in self.models[0].__fields__.keys()
            if field not in ["resources", "protocols", "id", "user_id", "env"]
        ]

        # Create table and add header
        self.table = Table(*field_names, show_header=True, header_style="bold cyan")

        # Add data rows
        for model in self.models:
            _model = model.dict()
            row_values = [str(_model[field]) for field in field_names]
            self.table.add_row(*row_values)

    def add_models(self):
        for space in self.models:
            pieces = [
                f"{k}: {v}\n"
                for k, v in space.dict().items()
                if k not in ["resources", "protocols", "env"] and v
            ]

            max_length = max([len(piece) for piece in pieces])
            splitter = "-" * max_length
            rich.print(f"{splitter}\n{''.join(pieces)}{splitter}")


class TyperSpaceAdaptor(ISpaceInvoker):
    def __init__(self, domain: ISpaceDomain):
        super().__init__()

        self.domain = domain
        self.console = Console()

        self.app = typer.Typer(
            cls=OrderCommands,
            help="Naas Space CLI",
            add_completion=False,
            no_args_is_help=True,
            pretty_exceptions_enable=False,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        # Include all commands
        # self.app.command()(self.list)
        self.app.command()(self.create)
        # self.app.command()(self.get)
        # self.app.command()(self.delete)
        # self.app.command()(self.update)
        # self.app.command()(self.add)

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
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
        image: str = typer.Option(..., "--image", help="Image of the space"),
        domain: str = typer.Option("", "--domain", "-d", help="Domain of the space"),
        env: str = typer.Option(
            None,
            "--env",
            help="Environment variables for the Space container",
        ),
        cpu: str = typer.Option(
            1,
            "--cpu",
            help="CPU utilization for the Space container",
        ),
        memory: str = typer.Option(
            "1Gi",
            "--memory",
            help="Memory utilization for the Space container",
        ),
        port: str = typer.Option(
            5080,
            "--port",
            help="Port for the Space container",
        ),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the space information as a table",
        ),
    ):
        """Create a space with the given specifications"""
        space = self.domain.create(
            name=name,
            domain=domain,
            containers=[
                {
                    "name": name,
                    "image": image,
                    "env": json.loads(env) if env else None,
                    "cpu": cpu,
                    "memory": memory,
                    "port": port,
                }
            ],
        )

        # Extract the data
        data = [space.space.dict().values()]

        # Define column headers using the determined widths
        headers = [key.upper() for key in space.space.dict().keys()]

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
        token: str = typer.Option(
            os.environ.get("NAAS_TOKEN", None), "--token", "-t", help="Naas token"
        ),
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
        namespace: str = typer.Option(
            "default", "--namespace", "-ns", help="Namespace of the space"
        ),
    ):
        if not token:
            raise typer.BadParameter(
                "Token is required, please provide a token or set NAAS_TOKEN environment variable"
            )
        try:
            self.domain.delete(name=name, namespace=namespace)
        except Exception as e:
            logger.debug(e)
            raise e

    def add():
        logger.debug("TyperSpaceAdaptor -> space -> add called")
        self.domain.add()

    def list(
        token: str = typer.Option(
            os.environ.get("NAAS_TOKEN", None), "--token", "-t", help="Naas token"
        ),
        namespace: str = typer.Option(
            "default", "--namespace", "-ns", help="Namespace of the space"
        ),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the space information as a table",
        ),
    ):
        if not token:
            raise typer.BadParameter(
                "Token is required, please provide a token or set NAAS_TOKEN environment variable"
            )
        try:
            spaces = self.domain.list(namespace=namespace)
            # print space table in the terminal
            if isinstance(spaces, List):
                if not spaces:
                    rich.print(
                        rich.panel.Panel(
                            "No spaces found for the given parameters",
                            style="magenta",
                        )
                    )
                    return
                if rich_preview:
                    self.console.print(PydanticTableModel(spaces).table)
                else:
                    PydanticTableModel(spaces).add_models()
            else:
                print(f"Unrecognized type: {type(spaces)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def get(
        token: str = typer.Option(
            os.environ.get("NAAS_TOKEN", None), "--token", "-t", help="Naas token"
        ),
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
        namespace: str = typer.Option(
            "default", "--namespace", "-ns", help="Namespace of the space"
        ),
        rich_preview: bool = typer.Option(
            os.environ.get("NAAS_CLI_RICH_PREVIEW", False),
            "--rich-preview",
            "-rp",
            help="Rich preview of the space information as a table",
        ),
    ):
        if not token:
            raise typer.BadParameter(
                "Token is required, please provide a token or set NAAS_TOKEN environment variable"
            )
        try:
            space = self.domain.get(name=name, namespace=namespace)
            # print space table in the terminal
            if isinstance(space, Space):
                if rich_preview:
                    self.console.print(PydanticTableModel([space]).table)
                else:
                    PydanticTableModel([space]).add_models()
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def update(
        token: str = typer.Option(
            os.environ.get("NAAS_TOKEN", None), "--token", "-t", help="Naas token"
        ),
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
        namespace: str = typer.Option(
            "default", "--namespace", "-ns", help="Namespace of the space"
        ),
        cpu: str = typer.Option(
            1,
            "--cpu",
            help="CPU utilization for the Space container",
        ),
        memory: str = typer.Option(
            "1Gi",
            "--memory",
            help="Memory utilization for the Space container",
        ),
        env: str = typer.Option(List[str], "--env", help="Environment variables"),
        image: str = typer.Option(
            "placeholder/placeholder:latest",
            "--image",
            help="Image of the space, e.g. placeholder/placeholder:latest",
        ),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the space information as a table",
        ),
    ):
        if not token:
            raise typer.BadParameter(
                "Token is required, please provide a token or set NAAS_TOKEN environment variable"
            )
        try:
            update_patch = {
                "cpu": cpu,
                "memory": memory,
                "env": env,
                "image": image,
            }

            space = self.domain.update(
                name=name,
                namespace=namespace,
                update_patch=update_patch,
            )
            # print space table in the terminal
            if isinstance(space, Space):
                if rich_preview:
                    self.console.print(PydanticTableModel([space]).table)
                else:
                    PydanticTableModel([space]).add_models()
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()
