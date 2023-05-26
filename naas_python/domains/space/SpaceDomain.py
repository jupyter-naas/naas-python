from .SpaceSchema import ISpaceDomain, ISpaceAdaptor, Space
from naas_python import logger
from typing import Callable


class SpaceDomain(ISpaceDomain):
    def __init__(self, adaptor: ISpaceAdaptor):
        self.adaptor = adaptor

    def execute_adaptor_method(self, method_name, **kwargs):
        logger.debug(f"SpaceDomain -> {method_name} called")
        try:
            if hasattr(self.adaptor, method_name):
                logger.debug(
                    f"SpaceDomain -> {method_name} found :: Proceeding to execute"
                )
                method = getattr(self.adaptor, method_name)
            else:
                logger.debug(
                    f"SpaceDomain -> {method_name} not found :: Raising AttributeError"
                )
                raise AttributeError(
                    f"Method '{method_name}' not found on adaptor '{self.adaptor.__class__.__name__}'"
                )

            if not isinstance(method, Callable):
                logger.debug(
                    f"SpaceDomain -> {method_name} not callable :: Raising AttributeError"
                )
                raise AttributeError(
                    f"Method '{method_name}' not callable on adaptor '{self.adaptor.__class__.__name__}'"
                )

            return method(**kwargs)
        except Exception as e:
            logger.debug(f"SpaceDomain -> {method_name} failed with error: {e}")
            raise e

    def add(self):
        self.execute_adaptor_method("add")

    def create(self, **kwargs):
        response = self.execute_adaptor_method("create", **kwargs)
        if isinstance(response, str):
            return response
        return Space(**response)

    def get(self, **kwargs):
        response = self.execute_adaptor_method("get", **kwargs)
        if isinstance(response, str):
            return response
        return Space(**response)

    def delete(self, **kwargs):
        self.execute_adaptor_method("delete", **kwargs)

    def list(self, **kwargs):
        self.execute_adaptor_method("list", **kwargs)

    def update(self, **kwargs):
        self.execute_adaptor_method("update", **kwargs)
