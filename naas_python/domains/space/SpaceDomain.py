from naas_python.domains.space.SpaceSchema import (
    ISpaceAdaptor,
    ISpaceDomain,
    Space,
    SpaceListResponse,
    SpaceConflictError,
)
from naas_python.domains.space.types.docker import build_and_push_docker_image

from functools import partial


class SpaceDomain(ISpaceDomain):
    def __init__(self, adaptor: ISpaceAdaptor):
        self.adaptor = adaptor

    def create(
        self,
        name: str,
        containers: list,
        domain: str,
    ) -> Space:
        response = self.adaptor.create_space(
            name=name, containers=containers, domain=domain
        )
        return Space(**response)

    def get(self, name: str):
        response = self.adaptor.get_space_by_name(name=name)
        return Space(**response)

    def delete(self, name: str):
        return self.adaptor.delete_space(name=name)

    def list(self, page_size: int, page_number: int) -> SpaceListResponse:
        response = self.adaptor.list_spaces(
            page_size=page_size, page_number=page_number
        )
        return SpaceListResponse(spaces=response)

    def update(self, name: str, containers: list, domain: str) -> Space:
        response = self.adaptor.update_space(
            name=name, containers=containers, domain=domain
        )
        return Space(**response)

    def add(
        self,
        space_name: str,
        space_type: str,
        dockerfile_path: str,
        docker_context: str,
        image: str,
        image_tag: str,
        containers: list,
        domain: str,
        registry_name: str,
        skip_registry: bool = False,
        skip_build: bool = False,
        ci_type: str = "github-actions",
        generate_ci: bool = False,
    ):
        """
        Add a new space and configure its settings, including building Docker images and setting up CI/CD.

        Example container configuration:

            {
                "name": "my-container",\n
                "image": "my-image:latest",\n
                "env": {"ENV_VARIABLE": "value"},\n
                "port": 8080,\n
                "CPU": "1",\n
                "memory": "512Mi"
            }

        Args:
            space_name (str): The name of the space.
            space_type (str): The type of the space, e.g., "docker".
            dockerfile_path (str): The path to the Dockerfile.
            docker_context (str): The path to the Docker context.
            image (str): The name of the Docker image.
            image_tag (str): The tag for the Docker image.
            containers (list): A list of dictionaries representing container configurations.
            domain (str): The domain of the space.
            registry_name (str): The name of the Docker registry.
            skip_registry (bool, optional): Whether to skip creating a Docker registry. Defaults to False.
            skip_build (bool, optional): Whether to skip the image build process. Defaults to False.
            ci_type (str, optional): The type of CI/CD configuration to generate. Defaults to "github-actions".
            generate_ci (bool, optional): Whether to generate CI/CD configuration. Defaults to False.

        Returns:
            None
        """

        # Initialize the stage object
        stage = {
            "progress": {
                "description": "",
                "advance": 0.0,
            },
            "registry_name": registry_name,
            "space_name": space_name,
            "space_type": space_type,
        }

        # Execute the child (step) functions
        progress_steps = []

        # Step 1: Create a new Registry if requested
        if not skip_registry:
            progress_steps.append(self._create_registry)

        # Step 2.a: Build and push image to registry container if requested
        if space_type == "docker":
            progress_steps.append(
                build_and_push_docker_image,
            )

        # Step 2.b: Create a new space on domain
        progress_steps.append(self._create_space)

        # Step 3: Generate CI/CD configuration if requested
        if generate_ci:
            progress_steps.append(self._generate_cicd_configuration)

        for step in progress_steps:
            yield step(**stage)

    #     if not image:
    #         containers[0]["image"] = f"{registry_name}:{image_tag}"

    def _create_registry(self, registry_name, space_type):
        yield {"description": "Creating Docker Registry...", "advance": 0}

        # Supposes that no registry exists for the given name, else retrieve it.
        try:
            _r = RegistryHandler.create(name=registry_name)
            registry = _r.registry
        except RegistryConflictError:
            print(
                f"A registry with the name '{registry_name}' already exists. Proceeding with existing registry."
            )
            _r = RegistryHandler.get(name=registry_name)
            registry = _r.registry

        yield {"description": "Docker Registry Created.", "advance": 0.5}

        # Get credentials for the registry (will create a credentials file if it doesn't exist)
        # and set up docker login for the registry (if type is docker)
        if space_type == "docker":
            yield {
                "description": "Retrieving credentials for Docker Registry...",
                "advance": 0.5,
            }
            self.docker_login(registry_name)
            yield {
                "description": "Docker Registry Credentials Retrieved.",
                "advance": 1,
            }

        yield {"description": "Docker Registry Created.", "advance": 1}

    # def _create_space(self, space_name, image, cpu, memory, container_port, domain):
    #     # space_task = progress.add_task("[cyan]Creating Naas Space...", total=1)
    #     # progress.update(space_task, advance=0.25)
    #     try:
    #         self.create(
    #             name=space_name,
    #             domain=domain,
    #             containers=[
    #                 {
    #                     "name": space_name,
    #                     "image": image,
    #                     "env": {},
    #                     "cpu": cpu,
    #                     "memory": memory,
    #                     "port": container_port,
    #                 }
    #             ],
    #         )
    #     except SpaceConflictError as e:
    #         # progress.print(
    #         #     f"[yellow]A space with the name '{space_name}' already exists. Proceeding with existing space.[/yellow]"
    #         # )
    #         self.get(name=space_name, rich_preview=False)
    #     # progress.update(space_task, advance=1)

    # def _generate_cicd_configuration(self):
    #     pass
