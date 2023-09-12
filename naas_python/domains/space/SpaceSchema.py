from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import Any

from naas_models.pydantic.space_p2p import *

from naas_python.utils.exceptions import NaasException

logger = getLogger(__name__)

# Secondary adaptor


class ISpaceAdaptor(metaclass=ABCMeta):
    @abstractmethod
    def update_space(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def create_space(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_space_by_name(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_spaces(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def delete_space(self, **kwargs) -> dict:
        raise NotImplementedError


# Domain


class ISpaceDomain(metaclass=ABCMeta):
    adaptor: ISpaceAdaptor

    @abstractmethod
    def create(self, **kwargs) -> SpaceCreationResponse:
        raise NotImplementedError

    @abstractmethod
    def update(self, **kwargs) -> SpaceUpdateResponse:
        raise NotImplementedError

    @abstractmethod
    def get_space_by_name(self, **kwargs) -> SpaceGetResponse:
        raise NotImplementedError

    @abstractmethod
    def list(self, **kwargs) -> SpaceListResponse:
        raise NotImplementedError

    @abstractmethod
    def delete(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add(self):
        raise NotImplementedError


# Primary Adaptor


class ISpaceInvoker(metaclass=ABCMeta):
    @abstractmethod
    def create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def list(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def add(self, **kwargs):
        raise NotImplementedError


# Exceptions


class SpaceValidationError(NaasException):
    pass


class SpaceConflictError(NaasException):
    pass


class SpaceNotFound(NaasException):
    pass
