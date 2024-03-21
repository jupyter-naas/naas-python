import typer
import logging
logging.basicConfig(level=logging.ERROR)

from naas_python.domains.registry.handlers.CLIRegistryHandler import (
    primaryAdaptor as typerRegistryAdaptor,
)

# from naas_python.domains import spaceCliAdaptor  # , registryCliAdaptor
from naas_python.domains.space.handlers.CLISpaceHandler import (
    primaryAdaptor as typerSpaceAdaptor,
)

# from naas_python.domains import secretCliAdaptor  # , secretCliAdaptor
from naas_python.domains.secret.handlers.CLISecretHandler import (
    primaryAdaptor as typerSecretAdaptor,
)

from naas_python.domains.storage.handlers.CLIStorageHandler import (
    primaryAdaptor as typerStorageAdaptor,
)

def _create_cli_app():
    app = typer.Typer(
        epilog="Found a bug? Report it at https://github.com/jupyter-naas/naas-python/issues",
        pretty_exceptions_show_locals=False,
        pretty_exceptions_short=True,
        # pretty_exceptions_enable=False,
    )

    # Registry domain's related commands
    app.add_typer(typerSpaceAdaptor.app, name="space")
    app.add_typer(typerRegistryAdaptor.app, name="registry")
    app.add_typer(typerSecretAdaptor.app, name="secret")
    app.add_typer(typerStorageAdaptor.app, name="storage")    

    return app


app = _create_cli_app()
