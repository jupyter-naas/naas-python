from ..adaptors.secondary.NaasRegistryAPIAdaptor import NaasRegistryAPIAdaptor
from ..RegistryDomain import RegistryDomain
from ..adaptors.primary.SDKRegistryAdaptor import SDKRegistryAdaptor

secondaryAdaptor = NaasRegistryAPIAdaptor()
domain = RegistryDomain(secondaryAdaptor)
primaryAdaptor = SDKRegistryAdaptor(domain)
