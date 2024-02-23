from ..adaptors.secondary.NaasSecretAPIAdaptor import NaasSecretAPIAdaptor
from ..SecretDomain import SecretDomain
from ..adaptors.primary.SDKSecretAdaptor import SDKSecretAdaptor

secondaryAdaptor = NaasSecretAPIAdaptor()
domain = SecretDomain(secondaryAdaptor)
primaryAdaptor = SDKSecretAdaptor(domain)
