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

from naas_python.domains.space.adaptors.primary.utils import PydanticTableModel
from naas_python.domains.space.SpaceSchema import ISpaceDomain, ISpaceInvoker, Space
from naas_python.utils.cicd import Pipeline
import docker

logger = getLogger(__name__)
docker_client = docker.from_env()


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

        # Include all commands
        self.app.command()(self.list)
        self.app.command()(self.create)
        self.app.command()(self.get)
        self.app.command()(self.delete)
        self.app.command()(self.update)
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
        container_port: str = typer.Option(
            5080, "--container-port", "-cp", help="Port for the Space container"
        ),
        generate_ci: bool = typer.Option(
            True, "--generate-ci", "-gci", help="Generate CI/CD configuration"
        ),
        ci_type: str = typer.Option(
            "github-actions",
            "--ci-type",
            "-ct",
            help="Type of CI/CD configuration to generate",
        ),
        cpu: str = typer.Option(
            2, "--cpu", "-c", help="CPU utilization for the Space container"
        ),
        memory: str = typer.Option(
            "2Gi", "--memory", "-m", help="Memory utilization for the Space container"
        ),
    ):
        # Step 1: Create a new Docker registry on space.naas.ai
        registry_name = f"{space_name}-registry"

        with Progress() as progress:
            registry_task = progress.add_task(
                "[cyan]Creating Docker Registry...", total=1
            )
            from naas_python.domains.registry.handlers import RegistryHandler

            _registry = RegistryHandler().create(name=registry_name)

            # Get credentials for the registry (will create a credentials file if it doesn't exist)
            _registry_credentials = RegistryHandler().get_credentials(
                name=registry_name
            )

        # Step 2: Create a new space on space.naas.ai
        with Progress() as progress:
            space_task = progress.add_task("[cyan]Creating Naas Space...", total=1)
            _space = self.create(
                name=space_name,
                domain=f"{space_name}.naas.ai",
                containers=[
                    {
                        "name": space_name,
                        "image": f"{registry_name}/{space_name}",
                        "env": {},
                        "cpu": cpu,
                        "memory": memory,
                        "port": container_port,
                    }
                ],
            )
            space_task.completed = True

        # Step 3: Generate CI/CD configuration if requested
        if generate_ci:
            pipeline = Pipeline(name=f"ci-{space_name}")

            # Check for naas_python cli help command
            pipeline.add_job(
                "Validate that naas_python works",
                [
                    "name: Validate that naas_python works",
                    "run: |",
                    "  naas_python --help",
                ],
            )

            # Check Naas Space status
            pipeline.add_job(
                "Check Naas Space status",
                [
                    "name: Check Naas Space status",
                    "run: |",
                    f"  naas_python space get --name { space_name }",
                ],
            )

            # Check Naas Registry status
            pipeline.add_job(
                "Check Naas Registry status",
                [
                    "name: Check Naas Registry status",
                    "run: |",
                    f"  naas_python registry get --name { registry_name }",
                ],
            )

            # Check Naas Registry credentials
            pipeline.add_job(
                "Check Naas Registry credentials and add to output",
                [
                    "name: Check Naas Registry credentials",
                    "run: |",
                    f"  naas_python registry get-credentials --name { registry_name }",
                    f"echo '$(cat {registry_name}-credentials.txt )' >> $GITHUB_OUTPUT",
                ],
            )

            # Add custom jobs for CI/CD configuration
            if space_type == "docker":
                docker_steps = [
                    "name: Build and Push Docker Image",
                    f'if: ${{ github.event_name == "push" }}',
                    "run: |",
                    "  docker build -t {{ registry_name }}/{{ space_name }} -f {{ dockerfile_path }} {{ docker_context }}",
                    "  docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD",
                    "  docker push {{ registry_name }}/{{ space_name }}",
                ]
                pipeline.add_job("Build and Push Docker Image", docker_steps)

            # Render the CI/CD configuration
            pipeline.render()

            self.console.print("[green]Generated CI/CD configuration.[/green]")
        else:
            # If generate_ci is not passed, build the Docker image using the docker package
            if space_type == "docker" and dockerfile_path and docker_context:
                self.console.print("[cyan]Building Docker Image...[/cyan]")
                try:
                    image, _ = docker_client.images.build(
                        path=docker_context,
                        dockerfile=dockerfile_path,
                        tag=f"{registry_name}/{space_name}",
                    )
                    self.console.print(
                        "[green]Docker Image Built Successfully![/green]"
                    )
                    # Push the image
                    docker_client.images.push(
                        repository=f"{registry_name}/{space_name}",
                        tag="latest",
                        auth_config={
                            "username": _registry_credentials.username,
                            "password": _registry_credentials.password,
                        },
                    )

                except docker.errors.BuildError:
                    self.console.print("[red]Failed to Build Docker Image![/red]")
                    return
                except docker.errors.APIError:
                    self.console.print("[red]Failed to Push Docker Image![/red]")
                    return
