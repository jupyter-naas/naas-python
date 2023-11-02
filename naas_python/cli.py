import typer

from naas_python.domains.registry.handlers.CLIRegistryHandler import (
    primaryAdaptor as typerRegistryAdaptor,
)

# from naas_python.domains import spaceCliAdaptor  # , registryCliAdaptor
from naas_python.domains.space.handlers.CLISpaceHandler import (
    primaryAdaptor as typerSpaceAdaptor,
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

    return app


app = _create_cli_app()
