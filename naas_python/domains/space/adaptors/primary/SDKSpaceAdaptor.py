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
        # Create container or get existing container credentials
        if space_type == "docker":
            # we need to call the registry domain api to get the credentials,
            # I am adding a dummy call until we sort out the registry domain integration
            container = {
                "registry": {
                    "host": "https://registry.naas.ai",
                    "username": "naas",
                    "password": "naas",
                },
                "image": "naas",
            }
            # container = self.domain.create_docker_container(
            #     space_name=space_name,
            #     dockerfile_path=dockerfile_path,
            #     docker_context=docker_context,
            #     container_port=container_port,
            # )
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

    def credentials(self, token: str = None) -> NAASCredentials:
        """
        Retrieves the NAAS credentials.
        If the `token` parameter is not provided, it attempts to load the token
        from the credentials file. If the file is not found or does not contain
        a valid token, an exception is raised.
        Args:
            token (str, optional): Authorization token for NAAS. Defaults to the value of
                the 'NAAS_TOKEN' environment variable.
        Returns:
            NAASCredentials: NAAS credentials.
        Raises:
            Exception: If the token is missing and cannot be loaded from the credentials file.
        """
        if not token:
            if os.environ.get("NAAS_TOKEN"):
                token = os.environ.get("NAAS_TOKEN")
            else:
                token = load_token_from_file()
        return NAASCredentials(token=token)

    def create(
        self,
        name: str,
        namespace: str,
        image: str,
        user_id: str,
        env: dict,
        resources: dict,
    ):
        try:
            space = self.domain.create(
                name=name,
                namespace=namespace,
                image=image,
                user_id=user_id,
                env=env,
                resources=resources,
            )
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def get(self, name: str, namespace: str):
        try:
            space = self.domain.get(name=name, namespace=namespace)
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def list(self, user_id: str, namespace: str):
        try:
            space = self.domain.list(user_id=user_id, namespace=namespace)
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()

    def delete(self, name: str, namespace: str):
        try:
            self.domain.delete(name=name, namespace=namespace)
        except Exception as e:
            print(e)
            raise e

    def update(
        self,
        name: str,
        namespace: str,
        image: str,
        env: dict,
        resources: dict,
        cpu: str,
        memory: str,
    ):
        try:
            space = self.domain.update(
                name=name,
                namespace=namespace,
                update_patch={
                    "image": image,
                    "cpu": cpu,
                    "memory": memory,
                    "env": env,
                    "resources": resources,
                },
            )
            # print space table in the terminal
            if isinstance(space, Space):
                return space
            else:
                print(f"Unrecognized type: {type(space)}")
        except NaasSpaceError as e:
            e.pretty_print()
