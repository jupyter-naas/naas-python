from abc import ABCMeta, abstractmethod


# Secondary adaptor

class ISpaceAdaptor(metaclass=ABCMeta):
    
    @abstractmethod
    def add(self):
        raise NotImplementedError

# Domain

class ISpaceDomain(metaclass=ABCMeta):
    
    adaptor : ISpaceAdaptor

    @abstractmethod
    def add(self):
        raise NotImplementedError

# Primary Adaptor

class ISpaceInvoker(metaclass=ABCMeta):
    pass