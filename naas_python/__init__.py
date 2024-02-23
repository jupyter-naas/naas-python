from .domains.registry.handlers.PythonHandler import primaryAdaptor as registry
from .domains.space.handlers.PythonHandler import primaryAdaptor as space
from .domains.secret.handlers.PythonHandler import primaryAdaptor as secret
from .utils.log import initialize_logging

logger = initialize_logging()
