import typer
from os import getenv
import sys
from naas_python.domains.space.handlers.CLISpaceAdaptor import (
    primaryAdaptor as spaceAdaptor,
)
from naas_python.domains.registry.handlers.CLIRegistryHandler import (
    primaryAdaptor as registryAdaptor,
)


# if getenv("NAAS_PYTHON_DEBUG", "False").lower() == "false":
#     sys.tracebacklimit = 0  # Disable traceback

app = typer.Typer(
    epilog="Found a bug? Report it at https://github.com/jupyter-naas/naas-python/issues ",
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
    # pretty_exceptions_enable=False,
)

app.add_typer(spaceAdaptor.app, name="space")

app.add_typer(registryAdaptor.app, name="registry")
