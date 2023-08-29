import json
import os
from typing import List

import rich
import typer
from click import Context
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from typer.core import TyperGroup
from typing_extensions import Annotated

from naas_python import logger
from naas_python.domains.registry.RegistryDomain import RegistryDomain
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

        self.app = typer.Typer(
            cls=OrderCommands,
            help="Naas Space CLI",
            add_completion=False,
            no_args_is_help=True,
            pretty_exceptions_enable=False,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        @self.app.command()
        def create(
            name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
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
            try:
                space = self.domain.create(
                    name=name,
                    containers=[
                        {
                            "name": name,
                            "image": image,
                            "env": json.loads(env) if env else None,
                            "cpu": cpu,
                            "memory": memory,
                            "port": 5080,
                        }
                    ],
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
        ):
            try:
                self.domain.delete(name=name)
            except Exception as e:
                logger.debug(e)
                raise e

        @self.app.command()
        def add(
            space_name: str,
            space_type: str = "docker",
            dockerfile_path: str = "Dockerfile",
            docker_context: str = ".",
            container_port: str = "8080",
            generate_ci: bool = True,
            ci_type: str = "github-actions",
            cpu: str = None,
            memory: str = None,
        ):
            """
            Add a new space with the provided specifications.
            Args:
                space_name (str): The name of the new space.
                space_type (str): The type of space to create.
                dockerfile_path (str): The path to the Dockerfile in the project.
                docker_context (str): The folder from which to build the container.
                container_port (str): The port on which the container will listen.
                generate_ci (bool): Whether to generate CI/CD configuration.
                ci_type (str): The type of CI for generating the configuration.
                cpu (str): The CPU request for the container to run.
                memory (str): The memory request for the container to run.
            """
            # Create registry if it doesn't exist
            from naas_python.domains.registry.handlers.PythonHandler import (
                primaryAdaptor as registry_primary_adaptor,
            )

            registry = registry_primary_adaptor.create(
                "naas-test",
            )
            # get registry credentials
            registry_credentials = registry_primary_adaptor.get_credentials(
                name="naas-test",
            )

            # Create container or get existing container credentials
            if space_type == "docker":
                container = {
                    "registry": registry_credentials,
                    "image": "naas",  # need to change this to the name of the image so we can build it
                }
            else:
                raise NotImplementedError(
                    f"Space type {space_type} is not supported yet"
                )

            # Create the space
            space = self.domain.create(
                name=space_name,
                containers=[container],
                cpu=cpu,
                memory=memory,
            )

            if generate_ci:
                # TODO: Generate the CI/CD configuration, part of another PR
                pass
                # self.domain.generate_ci(
                #     space_name=space_name,
                #     ci_type=ci_type,
                # )

            return space

        @self.app.command()
        def list(
            rich_preview: bool = typer.Option(
                False,
                "--rich-preview",
                "-rp",
                help="Rich preview of the space information as a table",
            ),
        ):
            try:
                spaces = self.domain.list()
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
            rich_preview: bool = typer.Option(
                os.environ.get("NAAS_CLI_RICH_PREVIEW", False),
                "--rich-preview",
                "-rp",
                help="Rich preview of the space information as a table",
            ),
        ):
            try:
                space = self.domain.get(name=name)
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
