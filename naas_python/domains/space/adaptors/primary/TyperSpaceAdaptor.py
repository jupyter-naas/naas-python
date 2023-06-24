from ...SpaceSchema import ISpaceInvoker, ISpaceDomain

import typer

from pathlib import Path
from types import SimpleNamespace
from naas_python.domains.authorization import write_token_to_file, load_token_from_file


class TyperSpaceAdaptor(ISpaceInvoker):
    app = typer.Typer()

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain

        @self.app.command()
        def add():
            print("TyperSpaceAdaptor add called")
            self.domain.add()

        @self.app.command()
        def list():
            print("TyperSpaceAdaptor list called")

    @app.callback()
    def authorization_callback(
        ctx: typer.Context,
        token: str = typer.Option(
            None,
            "--token",
            envvar="NAAS_TOKEN",
            help="User NAAS authorization token",
        ),
    ):
        # Check when the token is not provided as a command-line argument
        if not token:
            try:
                # Attempt to load the token from the credentials file
                token = load_token_from_file()
            except FileNotFoundError:
                typer.echo(
                    "Missing NAAS credentials file; pass --token or set NAAS_TOKEN as an environment variable"
                )
                raise typer.Exit(1)

        ctx.obj = SimpleNamespace(token=token)
