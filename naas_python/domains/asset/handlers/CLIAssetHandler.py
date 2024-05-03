
from naas_python.domains.asset.adaptors.secondary.NaasAssetAPIAdaptor import NaasAssetAPIAdaptor
from naas_python.domains.asset.AssetDomain import AssetDomain
from naas_python.domains.asset.adaptors.primary.TyperAssetAdaptor import TyperAssetAdaptor

import logging

secondaryAdaptor = NaasAssetAPIAdaptor()

domain = AssetDomain(secondaryAdaptor)

primaryAdaptor = TyperAssetAdaptor(domain)