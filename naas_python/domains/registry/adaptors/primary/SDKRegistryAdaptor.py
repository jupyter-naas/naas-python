import os

from rich.panel import Panel

from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryInvoker,
    RegistryCreationResponse,
    RegistryCredentialsResponse,
    RegistryGetResponse,
    RegistryListResponse,
)


class SDKRegistryAdaptor(IRegistryInvoker):
    domain: IRegistryDomain

    def __init__(self, domain: IRegistryDomain):
        self.domain = domain

    def create(self, name="") -> RegistryCreationResponse:
        """Create a registry with the given name"""
        registry = self.domain.create(name=name)
        return registry

    def list(self, page_size: int = 0, page_number: int = 0) -> RegistryListResponse:
        """List all registries for the current user"""
        registry_list = self.domain.list(page_size=page_size, page_number=page_number)
        return registry_list

    def get(self, name="") -> RegistryGetResponse:
        """Get a registry with the given name"""
        registry = self.domain.get_registry_by_name(name=name)
        return registry

    def delete(self, name="") -> None:
        """Delete a registry by name"""
        self.domain.delete(name=name)

    def get_credentials(self, name="") -> RegistryCredentialsResponse:
        """Get access credentials for registry"""
        credentials = self.domain.get_credentials(name=name)
        return credentials

    def docker_login(self, name="") -> None:
        """Execute Docker login for the specified registry"""
        registry = self.domain.get_registry_by_name(name=name)

        uri = registry.registry.uri
        response = self.domain.get_credentials(name=name)
        username = response.credentials.username
        password = response.credentials.password

        exec_code = os.system(
            f"echo '{password}' | docker login --username '{username}' --password-stdin '{uri}'"
        )
        if exec_code == 0:
            self.console.print(Panel.fit(f"You can now push containers to '{uri}'"))
