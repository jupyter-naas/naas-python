from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


# Secondary adaptor


class ISpaceAdaptor(metaclass=ABCMeta):
    @abstractmethod
    def add(self):
        raise NotImplementedError


@dataclass
class NAASCredentials:
    token: str


# Domain


class ISpaceDomain(metaclass=ABCMeta):
    adaptor: ISpaceAdaptor

    @abstractmethod
    def add(self):
        raise NotImplementedError


# Primary Adaptor


class ISpaceInvoker(metaclass=ABCMeta):
    pass
