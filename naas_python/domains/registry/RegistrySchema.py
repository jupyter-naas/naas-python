# Exception
from abc import ABCMeta, abstractmethod
from typing import Any, Callable

from naas_models.pydantic.registry_p2p import *
from rich.console import Console
from rich.panel import Panel

from naas_python import logger

# Secondary adaptor


class IRegistryAdaptor(metaclass=ABCMeta):
    @abstractmethod
    def add(self):
        raise NotImplementedError


# Domain


class IRegistryDomain(metaclass=ABCMeta):
    adaptor: IRegistryAdaptor

    def execute_adaptor_method(self, method_name, **kwargs):
        try:
            method = getattr(self.adaptor, method_name, None)
            if method is None:
                raise RegistryDomainError(
                    f"Method '{method_name}' not found on adaptor '{self.adaptor.__class__.__name__}'"
                )

            if not isinstance(method, Callable):
                raise RegistryDomainError(
                    f"Method '{method_name}' is not callable on adaptor '{self.adaptor.__class__.__name__}'"
                )

            return method(**kwargs)

        except Exception as e:
            raise e


# Primary Adaptor


class IRegistryInvoker(metaclass=ABCMeta):
    pass


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
            self.message, title="Error", title_align="left", border_style="bold red"
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
