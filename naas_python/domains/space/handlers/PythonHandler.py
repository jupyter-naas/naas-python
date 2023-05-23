from ..adaptors.secondary.NaasSpaceAPIAdaptor import NaasSpaceAPIAdaptor
from ..SpaceDomain import SpaceDomain
from ..adaptors.primary.SDKSpaceAdaptor import SDKSpaceAdaptor

secondaryAdaptor = NaasSpaceAPIAdaptor()
domain = SpaceDomain(secondaryAdaptor)
primaryAdaptor = SDKSpaceAdaptor(domain)
