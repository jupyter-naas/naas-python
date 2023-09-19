from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryAdaptor,
    RegistryListResponse,
    RegistryGetResponse,
    RegistryCreationResponse,
    RegistryCredentialsResponse,
)
from typing import Callable, Dict


class RegistryDomain(IRegistryDomain):
    def __init__(self, adaptor: IRegistryAdaptor):
        self.adaptor = adaptor

    def list(self, page_size: int, page_number: int) -> RegistryListResponse:
        response = self.adaptor.list_registries(
            page_size=page_size, page_number=page_number
        )
        return RegistryListResponse(**response)

    def create(
        self,
        name: str,
    ) -> RegistryCreationResponse:
        response = self.adaptor.create_registry(name=name)
        return RegistryCreationResponse(**response)

    def get_registry_by_name(self, name: str) -> RegistryGetResponse:
        response = self.adaptor.get_registry_by_name(name=name)
        return RegistryGetResponse(**response)

    def delete(
        self,
        name: str,
    ) -> Dict[str, str]:
        self.adaptor.delete_registry(name=name)
        return {"message": "Registry deleted successfully"}

    def get_credentials(
        self,
        name: str,
    ) -> RegistryCredentialsResponse:
        response = self.adaptor.get_registry_credentials(name=name)
        return RegistryCredentialsResponse(**response)
