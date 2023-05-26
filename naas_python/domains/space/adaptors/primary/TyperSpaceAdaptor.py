from ...SpaceSchema import ISpaceInvoker, ISpaceDomain, Space

import typer
from typer.core import TyperGroup
from click import Context
from rich import print
from rich.console import Console
import yaml
from rich import print
from naas_python import logger


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


class TyperExecutionException(Exception):
    pass


class TyperSpaceAdaptor(ISpaceInvoker):
    def __init__(self, domain: ISpaceDomain):
        self.domain = domain
        self.console = Console()
        self.app = typer.Typer(
            cls=OrderCommands,
            help="Naas Space CLI",
            add_completion=False,
            no_args_is_help=True,
            rich_markup_mode="rich",
            context_settings={"help_option_names": ["-h", "--help"]},
        )

        def load_config_file(config_path: str):
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
            return config

        @self.app.command()
        def create(
            name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
            namespace: str = typer.Option(
                "default", "--namespace", "-ns", help="Namespace of the space"
            ),
            image: str = typer.Option(
                "placeholder/placeholder:latest", "--image", help="Image of the space"
            ),
            user_id: str = typer.Option(
                None,
                "--user-id",
                help="User ID (UUID) of the user who created the Space",
            ),
            env: str = typer.Option(
                None,
                "--env",
                help="Environment variables for the Space container",
            ),
            resources: str = typer.Option(
                None,
                "--resources",
                help="Resources for CPU and Memory utilization for the Space container",
            ),
            # config: str = typer.Option(
            #     None,
            #     "--config",
            #     "-c",
            #     help="Configuration file path for the Space object parameters. Used to populate nested parameters.",
            #     # autocompletion=autocompletion_path,
            # ),
        ):
            logger.debug("TyperSpaceAdaptor -> space -> create called")

            # if config:
            #     config_path, config_name = str(config).split("@")
            #     config_args = load_config_file(config_path)[config_name]
            #     # Typer args take precedence over config file args
            #     # If the key is not in the typer args, then use the config file args
            #     for key, value in config_args.items():
            #         if key not in locals():
            #             locals()[key] = value

            try:
                space = self.domain.create(
                    name=name,
                    namespace=namespace,
                    image=image,
                    user_id=user_id,
                    env=env,
                    resources=resources,
                )
                if isinstance(space, Space):
                    logger.debug(f"Space created: {space} successfully")
                    # print_box(space)
                else:
                    logger.debug(f"Space creation failed: {space}")
            except TyperExecutionException as e:
                logger.debug(e)
                raise e

        @self.app.command()
        def add():
            logger.debug("TyperSpaceAdaptor -> space -> add called")
            self.domain.add()

        @self.app.command()
        def list():
            logger.debug("TyperSpaceAdaptor -> space -> list called")
            self.domain.list()

        @self.app.command()
        def get():
            logger.debug("TyperSpaceAdaptor -> space -> get called")
            self.domain.get()
