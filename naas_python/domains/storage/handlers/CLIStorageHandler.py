from ..adaptors.secondary.NaasStorageAPIAdaptor import NaasStorageAPIAdaptor
from ..StorageDomain import StorageDomain
from ..adaptors.primary.TyperStorageAdaptor import TyperStorageAdaptor

import logging

logging.debug("CliStorageHandler.py : Initializing secondaryAdaptor")
secondaryAdaptor = NaasStorageAPIAdaptor()

logging.debug("CliStorageHandler.py : Initializing domain")
domain = StorageDomain(secondaryAdaptor)

logging.debug("CliStorageHandler.py : Initializing primaryAdaptor")
primaryAdaptor = TyperStorageAdaptor(domain)