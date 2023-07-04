import json
import os
from typing import List
from pathlib import Path
from types import SimpleNamespace
from naas_python.authorization import write_token_to_file, load_token_from_file

import rich
import typer
import yaml
from click import Context
from naas_python import logger
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from typer.core import TyperGroup

from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceInvoker,
    NaasSpaceError,
    Space,
)


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
        self.domain = domain
        self.console = Console()

        def load_config_file(config_path: str):
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
            return config

        self.app = typer.Typer(
            cls=OrderCommands,
            help="Naas Space CLI",
            add_completion=False,
            no_args_is_help=True,
            pretty_exceptions_enable=False,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        def authorization_callback(
            token: str = typer.Option(
                None,
                "--token",
                envvar="NAAS_TOKEN",
                help="User NAAS authorization token",
            ),
        ):
            # Check when the token is not provided as a command-line argument
            if not token:
                try:
                    # Attempt to load the token from the credentials file
                    token = load_token_from_file()
                except FileNotFoundError:
                    typer.echo(
                        "Missing NAAS credentials file; pass --token or set NAAS_TOKEN as an environment variable"
                    )
                    raise typer.Exit(1)

        Token = typer.Option(..., callback=authorization_callback)

        @self.app.command()
        def create(
            token: str = Token,
            name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
            namespace: str = typer.Option(
                "default", "--namespace", "-ns", help="Namespace of the space"
            ),
            image: str = typer.Option(..., "--image", help="Image of the space"),
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
            rich_preview: bool = typer.Option(
                False,
                "--rich-preview",
                "-rp",
                help="Rich preview of the space information as a table",
            ),
        ):
            try:
                space = self.domain.create(
                    name=name,
                    namespace=namespace,
                    image=image,
                    env=env,
                    resources={"cpu": cpu, "memory": memory},
                    token=ctx.obj.token,
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

        @self.app.command()
        def delete(
            name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
            namespace: str = typer.Option(
                "default", "--namespace", "-ns", help="Namespace of the space"
            ),
        ):
            try:
                self.domain.delete(name=name, namespace=namespace)
            except Exception as e:
                logger.debug(e)
                raise e

        @self.app.command()
        def add():
            logger.debug("TyperSpaceAdaptor -> space -> add called")
            self.domain.add()

        @self.app.command()
        def list(
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

        @self.app.command()
        def get(
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

        @self.app.command()
        def update(
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
