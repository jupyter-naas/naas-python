import json
import os

from naas_python.domains.registry.RegistrySchema import RegistryConflictError
from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceInvoker,
    SpaceConflictError,
)
# from naas_python.utils.cicd import Pipeline


class SDKSpaceAdaptor(ISpaceInvoker):
    domain: ISpaceDomain

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain

    def create(
        self,
        name: str,
        containers: list,
        domain: str,
    ):
        """Create a space with the given name"""
        space = self.domain.create(
            name=name,
            containers=containers,
            domain=domain
        )
        return space

    def get(self, name: str):    
        """Get a space with the given name"""
        space = self.domain.get(name=name)
        return space

    def list(self):
        """List all spaces for the current user"""
        space_list = self.domain.list()
        return space_list    

    def delete(self, name: str):    
        """Delete a space by name"""
        self.domain.delete(name=name)


    def update(
        self,
        name: str,
        image: str,
        domain: str = None,
        env: dict = None,
        port: int = 5080,
        cpu: int = 2,
        memory: str = "2Gi",
    ):
        space = self.domain.update(
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
        return space

    def add(
        self,
        space_name: str,
        space_type: str = "docker",
        dockerfile_path: str = None,
        docker_context: str = None,
        container_port: str or int = 5080,
        generate_ci: bool = True,
        skip_registry: bool = False,
        registry_name: str = None,
        ci_type: str = "github-actions",
        image: str = None,
        cpu: str or int = 2,
        memory: str = "2Gi",
    ):
        """
        Adds a new space and generates a CI/CD configuration for management.
        If requested, a new Docker registry will also be created and the CI/CD
        configuration will be updated accordingly.
        """
        registry_name = registry_name if registry_name else f"{space_name}-registry"

        # Step 1: Create a new Registry on space.naas.ai if requested

        if not skip_registry:
            print(f"Creating Docker Registry '{registry_name}'...")
            from naas_python.domains.registry.handlers.PythonHandler import (
                primaryAdaptor as RegistryHandler,
            )

            # Supposes that no registry exists for the given name, else retrieve it.
            try:
                registry = RegistryHandler.create(name=registry_name)
            except RegistryConflictError:
                print(
                    f"A registry with the name '{registry_name}' already exists. Proceeding with existing registry."
                )
                registry = RegistryHandler.get(name=registry_name)

            # Get credentials for the registry (will create a credentials file if it doesn't exist)
            # and set up docker login for the registry (if type is docker)
            if space_type == "docker":
                print(f"Retrieving credentials for Docker Registry...")
                RegistryHandler.get_credentials(name=registry_name)

        # Step 2.a: Build and push image to registry container if requested:
        if space_type == "docker":
            print(f"Building Docker Image for '{space_name}'...")
            os.system(
                f"docker build -t {registry.registry.uri}:latest -f {dockerfile_path} {docker_context}"
            )

            print("Pushing Docker Image...")
            os.system(f"docker push {registry.registry.uri}:latest")

        # Step 2.b: Create a new space on space.naas.ai
        print(f"Creating Naas Space '{space_name}'...")
        try:
            self.domain.create(
                name=space_name,
                domain=f"{space_name}.naas.ai",
                containers=[
                    {
                        "name": space_name,
                        "image": image if image else f"{registry.registry.uri}:latest",
                        "env": {},
                        "cpu": cpu,
                        "memory": memory,
                        "port": container_port,
                    }
                ],
            )
        except SpaceConflictError as e:
            print(
                f"A space with the name '{space_name}' already exists. Proceeding with existing space."
            )
            self.domain.get(name=space_name)

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

            # Add custom jobs for CI/CD configuration
            if space_type == "docker":
                # Retrieve credentials from registry and login into docker
                pipeline.add_job(
                    "Login to Docker Registry",
                    [
                        "name: Login to Docker Registry",
                        "run: |",
                        f"  naas_python registry docker-login --name { registry_name }",
                    ],
                )

                try:
                    _build_command = f"  docker build -t {registry.registry.uri}:latest -f {dockerfile_path} {docker_context}"
                except ValueError as e:
                    raise ValueError(
                        "When space_type is 'docker', dockerfile_path and docker_context must be provided. Please provide these values and try again"
                    ) from e

                docker_steps = [
                    "name: Build and Push Docker Image",
                    f'if: ${{ github.event_name == "push" }}',
                    "run: |",
                    _build_command,
                    f"  docker push { registry.registry.uri }:latest",
                ]
                pipeline.add_job("Build and Push Docker Image", docker_steps)

            # Render the CI/CD configuration
            pipeline.render()

            print("Generated CI/CD configuration.")
