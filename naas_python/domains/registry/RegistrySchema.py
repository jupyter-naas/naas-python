# Exception
from abc import ABCMeta, abstractmethod
from typing import Any, Callable

from naas_models.pydantic.registry_p2p import *
from rich.console import Console
from rich.panel import Panel

from logging import getLogger

logger = getLogger(__name__)

# Secondary adaptor


class IRegistryAdaptor(metaclass=ABCMeta):
    @abstractmethod
    def create_registry(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_registry_by_name(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def list_registries(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete_registry(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_registry_credentials(self, **kwargs):
        raise NotImplementedError


# Domain


class IRegistryDomain(metaclass=ABCMeta):
    adaptor: IRegistryAdaptor

    @abstractmethod
    def list(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_registry_by_name(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, **kwargs):
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


class NaasRegistryError(Exception):
    def __init__(self, message, source=None):
        self.message = message
        self.source = source
        super().__init__(self.message)

    def __str__(self):
        return self.message

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        logger.debug(f"{self.__class__.__name__}: {self.message}")
        return super().__call__(*args, **kwds)

    def pretty_print(self):
        console = Console()
        panel = Panel(
            self.message,
            title=f"Error  [{self.__class__.__name__}]",
            title_align="left",
            border_style="bold red",
        )
        console.print(panel)


class TyperRegistryError(NaasRegistryError):
    pass


class RegistryAPIAdaptorError(NaasRegistryError):
    pass


class SDKRegistryAdaptorError(NaasRegistryError):
    pass


class RegistryDomainError(NaasRegistryError):
    pass
