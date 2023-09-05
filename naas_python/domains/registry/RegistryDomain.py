from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryAdaptor,
    Registry,
    RegistryDomainError,
    RegistryAPIAdaptorError,
)
from typing import Callable


class RegistryDomain(IRegistryDomain):
    def __init__(self, adaptor: IRegistryAdaptor):
        self.adaptor = adaptor

    def list(self, page_size: int, page_number: int):
        try:
            response = self.adaptor.list_registries(
                page_size=page_size, page_number=page_number
            )
            if isinstance(response, str):
                return response
            elif isinstance(response, dict) and "registries" in response.keys():
                return [Registry(**registry) for registry in response["registries"]]
            else:
                return response
        except RegistryAPIAdaptorError as e:
            raise RegistryDomainError(e.message)
        except Exception as e:
            raise RegistryDomainError(e) from e

    def create(
        self,
        name: str,
    ):
        try:
            response = self.adaptor.create_registry(name=name)
            if isinstance(response, str):
                return response
            return Registry(**response)
        except RegistryAPIAdaptorError as e:
            raise RegistryDomainError(e.message)
        except Exception as e:
            raise RegistryDomainError(e)

    def get_registry_by_name(self, name: str):
        try:
            response = self.adaptor.get_registry_by_name(name=name)
            if isinstance(response, str):
                return response
            elif isinstance(response, dict) and "registry" in response.keys():
                return Registry(**response["registry"])
            return Registry(**response)
        except RegistryAPIAdaptorError as e:
            raise RegistryDomainError(e.message)
        except Exception as e:
            raise RegistryDomainError(e)

    def delete(
        self,
        name: str,
    ):
        try:
            self.adaptor.delete_registry(name=name)
        except RegistryAPIAdaptorError as e:
            raise RegistryDomainError(e.message)
        except Exception as e:
            raise RegistryDomainError(e)

    def get_credentials(
        self,
        name: str,
    ):
        try:
            response = self.adaptor.get_registry_credentials(name=name)
            if isinstance(response, str):
                return response
            elif isinstance(response, dict) and "credentials" in response.keys():
                return response["credentials"]
            return response
        except RegistryAPIAdaptorError as e:
            raise RegistryDomainError(e.message)
        except Exception as e:
            raise RegistryDomainError(e)
