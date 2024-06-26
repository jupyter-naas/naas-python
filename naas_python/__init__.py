from .domains.registry.handlers.PythonHandler import primaryAdaptor as registry
from .domains.space.handlers.PythonHandler import primaryAdaptor as space
from .domains.secret.handlers.PythonHandler import primaryAdaptor as secret
from .domains.asset.handlers.PythonHandler import primaryAdaptor as asset
from .domains.storage.handlers.PythonHandler import primaryAdaptor as storage
from .utils.log import initialize_logging

logger = initialize_logging()
