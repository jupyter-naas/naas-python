from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryAdaptor,
    Registry,
    RegistryDomainError,
)
from naas_python import logger
from typing import Callable


class RegistryDomain(IRegistryDomain):
    def __init__(self, adaptor: IRegistryAdaptor):
        self.adaptor = adaptor

    def list(self, **kwargs):
        response = self.execute_adaptor_method("list_registries", **kwargs)
        if isinstance(response, str):
            return response
        elif isinstance(response, dict) and "registries" in response.keys():
            return [Registry(**registry) for registry in response["registries"]]
        else:
            return response

    def create(self, **kwargs):
        response = self.execute_adaptor_method("create_registry", **kwargs)
        if isinstance(response, str):
            return response
        return Registry(**response)

    def get_registry_by_name(self, **kwargs):
        response = self.execute_adaptor_method("get_registry_by_name", **kwargs)
        if isinstance(response, str):
            return response
        elif isinstance(response, dict) and "registry" in response.keys():
            return Registry(**response["registry"])
        else:
            return response

    def delete(self, **kwargs):
        return self.execute_adaptor_method("delete_registry", **kwargs)

    def get_credentials(self, **kwargs):
        response = self.execute_adaptor_method("get_registry_credentials", **kwargs)
        if isinstance(response, str):
            return response
        elif isinstance(response, dict) and "credentials" in response.keys():
            return response["credentials"]
        else:
            return response
