# Exception
from naas_python.utils.exceptions import NaasException

from abc import ABCMeta, abstractmethod
from typing import Any

from naas_models.pydantic.registry_p2p import *
from rich.console import Console
from rich.panel import Panel

from logging import getLogger

logger = getLogger(__name__)

# Secondary adaptor


class IRegistryAdaptor(metaclass=ABCMeta):
    @abstractmethod
    def create_registry(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_registry_by_name(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_registries(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def delete_registry(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_registry_credentials(self, **kwargs) -> dict:
        raise NotImplementedError


# Domain


class IRegistryDomain(metaclass=ABCMeta):
    adaptor: IRegistryAdaptor

    @abstractmethod
    def list(self, **kwargs) -> RegistryListResponse:
        raise NotImplementedError

    @abstractmethod
    def create(self, **kwargs) -> RegistryCreationResponse:
        raise NotImplementedError

    @abstractmethod
    def get_registry_by_name(self, **kwargs) -> RegistryGetResponse:
        raise NotImplementedError

    @abstractmethod
    def delete(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_credentials(self, **kwargs):
        raise NotImplementedError


# Primary Adaptor


class IRegistryInvoker(metaclass=ABCMeta):
    @abstractmethod
    def list(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_credentials(self, **kwargs):
        raise NotImplementedError


# Exceptions


class RegistryValidationError(NaasException):
    pass


class RegistryNotFound(NaasException):
    pass


class RegistryConflictError(NaasException):
    pass
