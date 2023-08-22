import typer

from naas_python.domains.space.handlers.CLISpaceAdaptor import (
    primaryAdaptor as spaceAdaptor,
)
from naas_python.domains.registry.handlers.CLIRegistryHandler import (
    primaryAdaptor as registryAdaptor,
)

app = typer.Typer(
    epilog="Found a bug? Report it at https://github.com/jupyter-naas/naas-python/issues "
)

app.add_typer(spaceAdaptor.app, name="space")

app.add_typer(registryAdaptor.app, name="registry")
