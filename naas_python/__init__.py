from .domains.registry.handlers.PythonHandler import primaryAdaptor as registry
from .domains.space.handlers.PythonHandler import primaryAdaptor as space
from .utils.log import initialize_logging

logger = initialize_logging()
