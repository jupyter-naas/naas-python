from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryInvoker,
    RegistryDomainError,
    TyperRegistryError,
)


class SDKRegistryAdaptor(IRegistryInvoker):
    domain: IRegistryDomain

    def __init__(self, domain: IRegistryDomain):
        self.domain = domain

    def create(self, name=""):
        """Create a registry"""
        try:
            response = self.domain.create(name=name)
            return response

        except RegistryDomainError as e:
            e.pretty_print()

        except Exception as e:
            raise TyperRegistryError(e) from e

    def list(self, page_size: int = 0, page_number: int = 0):
        """List all registries"""
        try:
            response = self.domain.list(page_size=page_size, page_number=page_number)
            return response
        except RegistryDomainError as e:
            e.pretty_print()

        except Exception as e:
            raise TyperRegistryError(e) from e

    def get(self, name=""):
        """Get a registry by name"""
        try:
            response = self.domain.get_registry_by_name(name=name)
            return response
        except RegistryDomainError as e:
            e.pretty_print()

        except Exception as e:
            raise TyperRegistryError(e) from e

    def delete(self, name=""):
        """Delete a registry by name"""
        try:
            response = self.domain.delete(name=name)
            return response
        except RegistryDomainError as e:
            e.pretty_print()

        except Exception as e:
            raise TyperRegistryError(e) from e

    def get_credentials(self, name=""):
        """Get a registry credentials by name"""
        try:
            response = self.domain.get_credentials(name=name)
            return response
        except RegistryDomainError as e:
            e.pretty_print()

        except Exception as e:
            raise TyperRegistryError(e) from e
