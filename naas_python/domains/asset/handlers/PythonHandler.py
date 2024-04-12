from naas_python.domains.asset.adaptors.secondary.NaasAssetAPIAdaptor import NaasAssetAPIAdaptor
from naas_python.domains.asset.AssetDomain import AssetDomain
from naas_python.domains.asset.adaptors.primary.SDKAssetAdaptor import SDKAssetAdaptor

secondaryAdaptor = NaasAssetAPIAdaptor()
domain = AssetDomain(secondaryAdaptor)
primaryAdaptor = SDKAssetAdaptor(domain)