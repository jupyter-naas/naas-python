from .SpaceSchema import ISpaceDomain, ISpaceAdaptor, Space, SpaceDomainError
from naas_python import logger
from typing import Callable


class SpaceDomain(ISpaceDomain):
    def __init__(self, adaptor: ISpaceAdaptor):
        self.adaptor = adaptor

    def execute_adaptor_method(self, method_name, **kwargs):
        try:
            if hasattr(self.adaptor, method_name):
                method = getattr(self.adaptor, method_name)
            else:
                raise SpaceDomainError(
                    f"Method '{method_name}' not found on adaptor '{self.adaptor.__class__.__name__}'"
                )

            if not isinstance(method, Callable):
                raise SpaceDomainError(
                    f"Method '{method_name}' not callable on adaptor '{self.adaptor.__class__.__name__}'"
                )

            return method(**kwargs)

        except Exception as e:
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
        elif isinstance(response, dict) and "space" in response.keys():
            return Space(**response["space"])
        else:
            return response

    def delete(self, **kwargs):
        return self.execute_adaptor_method("delete", **kwargs)

    def list(self, **kwargs):
        response = self.execute_adaptor_method("list", **kwargs)
        if isinstance(response, str):
            return response
        elif isinstance(response, dict) and "spaces" in response.keys():
            return [Space(**space) for space in response["spaces"]]
        else:
            return response

    def update(self, **kwargs):
        response = self.execute_adaptor_method("update", **kwargs)

        if isinstance(response, str):
            return response
        elif isinstance(response, dict) and "space" in response.keys():
            return Space(**response["space"])
        else:
            return response
