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
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from typer.core import TyperGroup
from typing_extensions import Annotated

from naas_python.domains.space.adaptors.primary.utils import PydanticTableModel
from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceInvoker,
    SpaceConflictError,
    SpaceListResponse,
    Space,
)
from naas_python.domains.registry.RegistrySchema import RegistryConflictError
from naas_python.utils.cicd.github import Pipeline

logger = getLogger(__name__)


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


class TyperPreview:
    def _print_container_info(self, container):
        """
        Print information about a container. This includes the container's name, image, environment variables, port, CPU, and memory.

        Args:
            container (Container): The container object to print information for. Attribute of a Space object.
        """
        container_info = [
            f"- Name: {container.name}",
            f"  Image: {container.image}",
            "  Environment Variables:",
        ]
        for key, value in container.env.items():
            container_info.append(f"    {key}: {value}")
        container_info.extend(
            [
                f"  Port: {container.port}",
                f"  CPU: {container.cpu}",
                f"  Memory: {container.memory}\n",
            ]
        )
        return container_info

    def space_preview(self, space: Space, rich_preview: bool = False):
        """
        Display a preview of a Space object.

        Args:
            space (Space): The Space object to preview.
            rich_preview (bool): If True, use rich formatting for the preview.

        """
        if rich_preview:
            self.console.print(PydanticTableModel([space]).table)
        else:
            self._print_space_info(space)

    def _print_space_info(self, space):
        """
        Print information about a Space. This includes the Space's name, user ID, ID, domain, and containers.

        Args:
            space (Space): The Space object to print information for.
        """
        space_info = [
            f"Name: {space.name}",
            f"User ID: {space.user_id}",
            f"ID: {space.id}",
            f"Domain: {space.domain}",
            "Containers:",
        ]
        for container in space.containers:
            space_info.extend(self._print_container_info(container))
        print("\n".join(space_info))

    def list_preview(self, space_list: SpaceListResponse, rich_preview: bool = False):
        """
        Display a preview of a list of Space objects.

        Args:
            space_list (SpaceListResponse): The response containing a list of Space objects.
            rich_preview (bool): If True, use rich formatting for the preview.
        """
        if not space_list.spaces:
            print("No matching results found.")
            return

        data = self._extract_space_data(space_list)
        headers = [key.upper() for key in data[0].keys()]

        if rich_preview:
            self._print_rich_table(data, headers)
        else:
            self._print_plain_table(data, headers)

    def _extract_space_data(self, space_list):
        """
        Extract and format space data from a SpaceListResponse.

        Args:
            space_list (SpaceListResponse): The response containing a list of Space objects.

        Returns:
            List[dict]: A list of dictionaries containing formatted space data.
        """
        data = []
        for space in space_list.spaces:
            space_dict = space.dict()
            space_dict.pop("containers", None)
            for key, value in space_dict.items():
                if isinstance(value, UUID):
                    space_dict[key] = str(value)
            data.append(list(space_dict.values()))
        return data

    def _print_rich_table(self, data, headers):
        """
        Print a rich-formatted table.

        Args:
            data (List[dict]): List of dictionaries containing table data.
            headers (list): List of table headers.
        """
        table = Table(show_header=True, header_style="bold")
        for header in headers:
            table.add_column(header, justify="center")
        for row in data:
            table.add_row(*row)
        self.console.print(table)

    def _print_plain_table(self, data, headers):
        """
        Print a plain-formatted table.

        Args:
            data (List[dict]): List of dictionaries containing table data.
            headers (list): List of table headers.
        """
        column_widths = [max(len(str(item)) for item in col) for col in zip(*data)]
        header_format = "  ".join(
            f"{header:<{width}}" for header, width in zip(headers, column_widths)
        )
        print(header_format)
        for row in data:
            row_format = "  ".join(
                f"{str(item):<{width}}" for item, width in zip(row, column_widths)
            )
            print(row_format)


class TyperSpaceAdaptor(ISpaceInvoker, TyperPreview):
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
        self.app.command()(self.list)
        self.app.command()(self.create)
        self.app.command()(self.get)
        self.app.command()(self.delete)
        self.app.command()(self.update)
        self.app.command()(self.add)

    def create(
        self,
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
        image: str = typer.Option(..., "--image", help="Image of the space"),
        domain: str = typer.Option("", "--domain", "-d", help="Domain of the space"),
        env: str = typer.Option(
            {},
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
                    "env": json.loads(env) if env else {},
                    "cpu": cpu,
                    "memory": memory,
                    "port": port,
                }
            ],
        )

        self.space_preview(space, rich_preview=rich_preview)

    def get(
        self,
        name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
        rich_preview: bool = typer.Option(
            False,
            "--rich-preview",
            "-rp",
            help="Rich preview of the space information as a table",
        ),
    ):
        """Get a space with the given name"""
        space = self.domain.get(name=name)

        self.space_preview(space, rich_preview=rich_preview)

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

        self.space_preview(space, rich_preview=rich_preview)

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

        self.list_preview(space_list, rich_preview=rich_preview)

    def add(
        self,
        space_name: str = typer.Option(
            ..., "--space-name", "-sn", help="Name of the space"
        ),
        space_type: str = typer.Option(
            "docker", "--space-type", "-st", help="Type of the space"
        ),
        dockerfile_path: str = typer.Option(
            None, "--dockerfile-path", "-dfp", help="Path to the Dockerfile"
        ),
        docker_context: str = typer.Option(
            None, "--docker-context", "-dc", help="Path to the Docker context"
        ),
        image_tag: str = typer.Option(
            "latest", "--image-tag", "-it", help="Tag for the Docker image"
        ),
        container_port: str = typer.Option(
            5080, "--container-port", "-cp", help="Port for the Space container"
        ),
        generate_ci: bool = typer.Option(
            True, "--generate-ci", "-gci", help="Generate CI/CD configuration"
        ),
        skip_registry: bool = typer.Option(
            False, "--skip-registry", "-sr", help="Skip creating a Docker registry"
        ),
        registry_name: str = typer.Option(
            None,
            "--registry-name",
            help="Name of the registry, required if skip_registry is False",
        ),
        ci_type: str = typer.Option(
            "github-actions",
            "--ci-type",
            "-ct",
            help="Type of CI/CD configuration to generate",
        ),
        image: str = typer.Option(
            None,
            "--image",
            "-i",
            help="Image of the space, required if space_type 'docker' is not provided",
        ),
        cpu: str = typer.Option(
            2, "--cpu", "-c", help="CPU utilization for the Space container"
        ),
        memory: str = typer.Option(
            "2Gi", "--memory", "-m", help="Memory utilization for the Space container"
        ),
    ):
        """
        Adds a new space and generates a CI/CD configuration for management.
        If requested, a new Docker registry will also be created and the CI/CD
        configuration will be updated accordingly.
        """
        registry_name = registry_name if registry_name else f"{space_name}-registry"

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            transient=True,
        ) as progress:
            for stage in self.domain.add():
                task = progress.add_task("[cyan] Instantiating stages.", total=1)

                progress.update(
                    task,
                    description=stage.get("description"),
                    advance=stage.get("advance"),
                )

        # # Step 1: Create a new Registry on space.naas.ai if requested

        # if not skip_registry:
        #     with Progress() as progress:
        #         registry_task = progress.add_task(
        #             "[cyan]Creating Docker Registry...", total=1
        #         )
        #         progress.update(registry_task, advance=0.25)
        #         from naas_python.domains.registry.handlers.PythonHandler import (
        #             primaryAdaptor as RegistryHandler,
        #         )

        #         # Supposes that no registry exists for the given name, else retrieve it.
        #         try:
        #             _r = RegistryHandler.create(name=registry_name)
        #             registry = _r.registry
        #         except RegistryConflictError:
        #             progress.print(
        #                 f"[yellow]A registry with the name '{registry_name}' already exists. Proceeding with existing registry.[/yellow]"
        #             )
        #             _r = RegistryHandler.get(name=registry_name)
        #             registry = _r.registry

        #         progress.update(registry_task, advance=0.5)

        #         # Get credentials for the registry (will create a credentials file if it doesn't exist)
        #         # and set up docker login for the registry (if type is docker)
        #         if space_type == "docker":
        #             progress.print(
        #                 f"[cyan]Retrieving credentials for Docker Registry...[/cyan]"
        #             )
        #             RegistryHandler.docker_login(name=registry_name)
        #             progress.update(registry_task, advance=0.75)

        #         progress.update(registry_task, advance=1)

        # # Step 2.a: Build and push image to registry container if requested:
        # if space_type == "docker":
        #     with Progress() as progress:
        #         build_task = progress.add_task(
        #             "[cyan]Building Docker Image...", total=1
        #         )
        #         os.system(
        #             f"docker build -t my_docker_image -f {dockerfile_path} {docker_context}"
        #         )
        #         os.system(f"docker tag my_docker_image {registry.uri}:{image_tag}")
        #         progress.update(build_task, advance=0.5)

        #         progress.print("[cyan]Pushing Docker Image... [/cyan]")
        #         os.system(f"docker push {registry.uri}:{image_tag}")
        #         progress.update(build_task, advance=1)

        # # Step 2.b: Create a new space on space.naas.ai
        # with Progress() as progress:
        #     space_task = progress.add_task("[cyan]Creating Naas Space...", total=1)
        #     progress.update(space_task, advance=0.25)
        #     try:
        #         self.create(
        #             name=space_name,
        #             image=image if image else f"{registry.uri}:{image_tag}",
        #             domain=f"{space_name}.naas.ai",
        #             env={},
        #             cpu=cpu,
        #             memory=memory,
        #             port=container_port,
        #             rich_preview=False,
        #         )
        #     except SpaceConflictError as e:
        #         progress.print(
        #             f"[yellow]A space with the name '{space_name}' already exists. Proceeding with existing space.[/yellow]"
        #         )
        #         self.get(name=space_name, rich_preview=False)
        #     progress.update(space_task, advance=1)

        # # Step 3: Generate CI/CD configuration if requested
        # if generate_ci:
        #     pipeline = Pipeline(name=f"ci-{space_name}")

        #     # Check for naas_python cli help command
        #     pipeline.add_job(
        #         "Validate that naas_python works",
        #         [
        #             "name: Validate that naas_python works",
        #             "run: |",
        #             "  naas_python --help",
        #         ],
        #     )

        #     # Check Naas Space status
        #     pipeline.add_job(
        #         "Check Naas Space status",
        #         [
        #             "name: Check Naas Space status",
        #             "run: |",
        #             f"  naas_python space get --name { space_name }",
        #         ],
        #     )

        #     # Check Naas Registry status
        #     pipeline.add_job(
        #         "Check Naas Registry status",
        #         [
        #             "name: Check Naas Registry status",
        #             "run: |",
        #             f"  naas_python registry get --name { registry_name }",
        #         ],
        #     )

        #     # Add custom jobs for CI/CD configuration
        #     if space_type == "docker":
        #         # Retrieve credentials from registry and login into docker
        #         pipeline.add_job(
        #             "Login to Docker Registry",
        #             [
        #                 "name: Login to Docker Registry",
        #                 "run: |",
        #                 f"  naas_python registry docker-login --name { registry_name }",
        #             ],
        #         )

        #         try:
        #             _build_command = f"  docker build -t {registry.uri}:latest -f {dockerfile_path} {docker_context}"
        #         except ValueError as e:
        #             raise ValueError(
        #                 "When space_type is 'docker', dockerfile_path and docker_context must be provided. Please provide these values and try again"
        #             ) from e

        #         docker_steps = [
        #             "name: Build and Push Docker Image",
        #             f'if: ${{ github.event_name == "push" }}',
        #             "run: |",
        #             _build_command,
        #             f"  docker push { registry.uri }:latest",
        #         ]
        #         pipeline.add_job("Build and Push Docker Image", docker_steps)

        #     # Render the CI/CD configuration
        #     pipeline.render()

        #     progress.print("[green]Generated CI/CD configuration.[/green]")
