from ..adaptors.secondary.NaasRegistryAPIAdaptor import NaasRegistryAPIAdaptor
from ..RegistryDomain import RegistryDomain
from ..adaptors.primary.TyperRegistryAdaptor import TyperRegistryAdaptor

secondaryAdaptor = NaasRegistryAPIAdaptor()
domain = RegistryDomain(secondaryAdaptor)
primaryAdaptor = TyperRegistryAdaptor(domain)
