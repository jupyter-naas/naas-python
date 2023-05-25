from ...SpaceSchema import ISpaceInvoker, ISpaceDomain, Space

import typer
from typer.core import TyperGroup
from click import Context
from rich import print
from rich.box import Box
from rich.console import Console


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

        @self.app.command()
        def create(
            name: str = typer.Option(..., "--name", "-n", help="Name of the space"),
            namespace: str = typer.Option(
                ..., "--namespace", "-ns", help="Namespace of the space"
            ),
            image: str = typer.Option(..., "--image", help="Image of the space"),
        ):
            print("TyperSpaceAdaptor -> space -> create called")
            try:
                space = self.domain.create(
                    name=name,
                    namespace=namespace,
                    image=image,
                )
                if isinstance(space, Space):
                    print(f"Space created: {space} successfully")
                    box = Box(
                        space,
                        title="Space Details",
                        style="bold green",
                        title_style="bold white",
                        padding=(1, 2),
                    )
                    self.console.print(box)
                else:
                    print(f"Space creation failed: {space}")
            except TyperExecutionException as e:
                print(e)
                raise e

        @self.app.command()
        def add():
            print("TyperSpaceAdaptor -> space -> add called")
            self.domain.add()

        @self.app.command()
        def list():
            print("TyperSpaceAdaptor -> space -> list called")
            self.domain.list()
