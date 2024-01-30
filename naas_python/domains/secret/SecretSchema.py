from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import Any

from naas_models.pydantic.secret_p2p import *

from naas_python.utils.exceptions import NaasException

logger = getLogger(__name__)

# Secondary adaptor


class ISecretAdaptor(metaclass=ABCMeta):

    @abstractmethod
    def create_secret(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_secrets(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def delete_secret(self, **kwargs) -> dict:
        raise NotImplementedError


# Domain


class ISecretDomain(metaclass=ABCMeta):
    adaptor: ISecretAdaptor

    @abstractmethod
    def create(self, **kwargs) -> SecretCreateRequest:
        raise NotImplementedError

    @abstractmethod
    def get(self, **kwargs) -> SecretGetResponse:
        raise NotImplementedError

    @abstractmethod
    def list(self, **kwargs) -> SecretListResponse:
        raise NotImplementedError

    @abstractmethod
    def delete(self, **kwargs) -> str:
        raise NotImplementedError


# Primary Adaptor


class ISecretInvoker(metaclass=ABCMeta):
    @abstractmethod
    def create(self, **kwargs):
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


# Exceptions
class SecretValidationError(NaasException):
    pass
class SecretConflictError(NaasException):
    pass
class SecretNotFound(NaasException):
    pass