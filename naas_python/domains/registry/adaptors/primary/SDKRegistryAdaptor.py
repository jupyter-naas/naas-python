from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    IRegistryInvoker,
    NaasRegistryError,
    Registry,
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
        except NaasRegistryError as e:
            raise e
        except Exception as e:
            raise e

    def list(self):
        """List all registries"""
        try:
            response = self.domain.list()
            return response
        except NaasRegistryError as e:
            raise e
        except Exception as e:
            raise e

    def get(self, name=""):
        """Get a registry by name"""
        try:
            response = self.domain.get_registry_by_name(name=name)
            return response
        except NaasRegistryError as e:
            raise e
        except Exception as e:
            raise e

    def delete(self, name=""):
        """Delete a registry by name"""
        try:
            response = self.domain.delete(name=name)
            return response
        except NaasRegistryError as e:
            raise e
        except Exception as e:
            raise e

    def get_credentials(self, name=""):
        """Get a registry credentials by name"""
        try:
            response = self.domain.get_credentials(name=name)
            return response
        except NaasRegistryError as e:
            raise e
        except Exception as e:
            raise e
