import typer
from .domains.space.handlers.CLISpaceAdaptor import primaryAdaptor

app = typer.Typer()

app.add_typer(primaryAdaptor.app, name='space')
