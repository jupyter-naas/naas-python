from pathlib import Path
from .utils.log import initialize_logging

logger = initialize_logging()

__ROOT_DIR__ = Path(__file__).parents[1].absolute()

# If the package is run as a script, run the main function to load the CLI.
if __name__ == "__main__":
    from naas_python.main import main

    main()
else:
    # Else use it as a library.
    from .domains.space.handlers.PythonHandler import primaryAdaptor as __space

    space = __space

    from .domains.registry.handlers.PythonHandler import primaryAdaptor as __registry

    registry = __registry
