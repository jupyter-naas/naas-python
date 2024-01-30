from ..adaptors.secondary.NaasSecretAPIAdaptor import NaasSecretAPIAdaptor
from ..SecretDomain import SecretDomain
from ..adaptors.primary.TyperSecretAdaptor import TyperSecretAdaptor

import logging

logging.debug("CliSecretHandler.py : Initializing secondaryAdaptor")
secondaryAdaptor = NaasSecretAPIAdaptor()

logging.debug("CliSecretHandler.py : Initializing domain")
domain = SecretDomain(secondaryAdaptor)

logging.debug("CliSecretHandler.py : Initializing primaryAdaptor")
primaryAdaptor = TyperSecretAdaptor(domain)