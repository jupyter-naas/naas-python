import json
import os

from naas_python.authorization import (
    NAASCredentials,
    load_token_from_file,
)
from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceInvoker,
    NaasSpaceError,
    Space,
)


class SDKSpaceAdaptor(ISpaceInvoker):
    domain: ISpaceDomain

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain

    def add(
        self,
        space_name: str,
        space_type: str,
        dockerfile_path: str,
        docker_context: str,
        container_port: str,
        generate_ci: bool,
        ci_type: str,
        cpu: str,
        memory: str,
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
            raise NotImplementedError(f"Space type {space_type} is not supported yet")

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

    def create(
        self,
        name: str,
        image: str,
        env: dict,
        cpu: int,
        memory: int,
        port: int = 5080,
        domain: str = "",
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
                        "port": port,
                    }
                ],
            )
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def get(self, name: str):
        try:
            space = self.domain.get(name=name)
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def list(self):
        try:
            space = self.domain.list()
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def delete(self, name: str):
        try:
            self.domain.delete(name=name)
        except Exception as e:
            print(e)
            raise e

    def update(
        self,
        name: str,
        image: str,
        env: dict,
        cpu: int,
        memory: int,
        port: int = 5080,
    ):
        try:
            update_patch = {
                "cpu": cpu,
                "memory": memory,
                "env": env,
                "image": image,
                "port": port,
            }

            space = self.domain.update(
                name=name,
                update_patch=update_patch,
            )
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()
