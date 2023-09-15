import json
import os
from logging import getLogger
from typing import List
from uuid import UUID

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
from naas_python.utils import render_cicd_jinja_template


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


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

        # @self.app.command()
        # def generate_ci(
        #     ciprovider: str = typer.Option("GitHub", help="Name of the CI/CD provider"),
        #     space_name: str = typer.Option(
        #         ..., "--space-name", "-sn", help="Name of the space"
        #     ),
        #     registry_name: str = typer.Option(
        #         ..., "--registry-name", "-rn", help="Name of the registry"
        #     ),
        #     docker_context: str = typer.Option(
        #         ..., "--context", "-c", help="Docker context"
        #     ),
        #     dockerfile_path: str = typer.Option(
        #         ..., "--dockerfile-path", "-dfp", help="Dockerfile path"
        #     ),
        # ):
        #     rendered_template = render_cicd_jinja_template(
        #         docker_context=docker_context,
        #         dockerfile_path=dockerfile_path,
        #         registry_name=registry_name,
        #         space_name=space_name,
        #     )
        #     os.makedirs(".github/workflows", exist_ok=True)

        #     with open(".github/workflows/main.yml", "w") as file:
        #         file.write(rendered_template)

        @self.app.command()
        def create(
            token: str = typer.Option(
                os.environ.get("NAAS_TOKEN", None),
                "--token",
                "-t",
                help="Naas token",
                show_default=False,
            ),
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
            if not token:
                raise typer.BadParameter(
                    "Token is required, please provide a token or set NAAS_TOKEN environment variable"
                )
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
                    token=token,
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

    def _print_container_info(self, container):
        print(f"- Name: {container.name}")
        print(f"  Image: {container.image}")
        print("  Environment Variables:")
        for key, value in container.env.items():
            print(f"    {key}: {value}")
        print(f"  Port: {container.port}")
        print(f"  CPU: {container.cpu}")
        print(f"  Memory: {container.memory}\n")

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

        if rich_preview:
            self.console.print(PydanticTableModel([space]).table)

        else:
            print(f"Name: {space.name}")
            print(f"User ID: {space.user_id}")
            print(f"ID: {space.id}")
            print(f"Domain: {space.domain}")
            print("Containers:")
            for container in space.containers:
                self._print_container_info(container)

    def get(
        self,
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
        rich_preview: bool = typer.Option(
            os.environ.get("NAAS_CLI_RICH_PREVIEW", False),
            "--rich-preview",
            "-rp",
            help="Rich preview of the space information as a table",
        ),
    ):
        """Get a space with the given name"""
        space = self.domain.get(name=name)

        if rich_preview:
            self.console.print(PydanticTableModel([space]).table)

        else:
            print(f"Name: {space.name}")
            print(f"User ID: {space.user_id}")
            print(f"ID: {space.id}")
            print(f"Domain: {space.domain}")
            print("Containers:")
            for container in space.containers:
                self._print_container_info(container)

    def update(
        self,
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
        domain: str = typer.Option(
            None,
            "--domain",
            "-d",
            help="Domain of the space",
        ),
        cpu: str = typer.Option(
            ...,
            "--cpu",
            help="CPU utilization for the Space container",
        ),
        memory: str = typer.Option(
            ...,
            "--memory",
            help="Memory utilization for the Space container",
        ),
        env: str = typer.Option(None, "--env", help="Environment variables"),
        image: str = typer.Option(
            ...,
            "--image",
            help="Image of the space, e.g. placeholder/placeholder:latest",
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
        """Update a space with the given specifications"""

        space = self.domain.update(
            name=name,
            domain=domain,
            containers=[
                {
                    "name": name,
                    "image": image,
                    "env": json.loads(env) if env else {},
                    "cpu": cpu,
                    "memory": memory,
                    "port": port,
                }
            ],
        )

        if rich_preview:
            self.console.print(PydanticTableModel([space]).table)

        else:
            print(f"Name: {space.name}")
            print(f"User ID: {space.user_id}")
            print(f"ID: {space.id}")
            print(f"Domain: {space.domain}")
            print("Containers:")
            for container in space.containers:
                self._print_container_info(container)

    def delete(
        self,
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
    ):
        self.domain.delete(name=name)

        print(f"Space {name} deleted successfully")

    def list(
        self,
        page_size: int = typer.Option(0, help="Size of each page of results"),
        page_number: int = typer.Option(0, help="Target page number of results"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the space information as a table",
        ),
    ):
        """List all spaces for the current user"""
        space_list = self.domain.list(page_size=page_size, page_number=page_number)

        data = []

        # Extract the data and headers
        for space in space_list.spaces:
            _space_dict = space.dict()
            _space_dict.pop("containers", None)  # Remove "containers" key if it exists

            # Convert UUID values to strings
            for key, value in _space_dict.items():
                if isinstance(value, UUID):
                    _space_dict[key] = str(value)

            data.append(list(_space_dict.values()))  # Append a list of values to data

        headers = [key.upper() for key in _space_dict.keys()]

        if len(data) == 0:
            print("No matching results found.")
            return

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

    def add(self):
        logger.debug("TyperSpaceAdaptor -> space -> add called")
        self.domain.add()
