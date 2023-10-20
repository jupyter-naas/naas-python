from ..adaptors.secondary.NaasSpaceAPIAdaptor import NaasSpaceAPIAdaptor
from ..SpaceDomain import SpaceDomain
from ..adaptors.primary.TyperSpaceAdaptor import TyperSpaceAdaptor

import logging

logging.debug("CliSpaceHandler.py : Initializing secondaryAdaptor")
secondaryAdaptor = NaasSpaceAPIAdaptor()

logging.debug("CliSpaceHandler.py : Initializing domain")
domain = SpaceDomain(secondaryAdaptor)

logging.debug("CliSpaceHandler.py : Initializing primaryAdaptor")
primaryAdaptor = TyperSpaceAdaptor(domain)
