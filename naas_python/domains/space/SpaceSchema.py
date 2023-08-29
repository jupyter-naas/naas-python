from abc import ABCMeta, abstractmethod
from typing import Any
from naas_models.pydantic.space_p2p import *
from naas_python import logger
from typing import List, Optional
from pydantic import BaseModel

# Secondary adaptor


class ISpaceAdaptor(metaclass=ABCMeta):
    @abstractmethod
    def add(self):
        raise NotImplementedError


# Domain


class ISpaceDomain(metaclass=ABCMeta):
    adaptor: ISpaceAdaptor

    @abstractmethod
    def add(self):
        raise NotImplementedError


# Primary Adaptor


class ISpaceInvoker(metaclass=ABCMeta):
    pass


# Exception

from rich.console import Console
from rich.panel import Panel


class NaasSpaceError(Exception):
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


class TyperSpaceError(NaasSpaceError):
    pass


class SpaceAPIAdaptorError(NaasSpaceError):
    pass


class SDKSpaceAdaptorError(NaasSpaceError):
    pass


class SpaceDomainError(NaasSpaceError):
    pass


class SpaceDTO(BaseModel):
    name: str
    image: str
    env: Optional[str] = None
    cpu: str = "1"
    memory: str = "1Gi"
    port: str = "5080"
