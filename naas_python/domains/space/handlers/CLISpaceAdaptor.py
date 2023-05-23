from ..adaptors.secondary.NaasSpaceAPIAdaptor import NaasSpaceAPIAdaptor
from ..SpaceDomain import SpaceDomain
from ..adaptors.primary.TyperSpaceAdaptor import TyperSpaceAdaptor

secondaryAdaptor = NaasSpaceAPIAdaptor()
domain = SpaceDomain(secondaryAdaptor)
primaryAdaptor = TyperSpaceAdaptor(domain)