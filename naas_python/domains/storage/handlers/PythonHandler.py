from ..adaptors.secondary.NaasStorageAPIAdaptor import NaasStorageAPIAdaptor
from naas_python.domains.storage.adaptors.secondary.providers.S3StorageProviderAdaptor import S3StorageProviderAdaptor
from ..StorageDomain import StorageDomain
from ..adaptors.primary.SDKStorageAdaptor import SDKStorageAdaptor

secondaryAdaptor = NaasStorageAPIAdaptor()

s3 = S3StorageProviderAdaptor()
#azure = AzureStorageProviderAdaptor()
storage_provider_adaptors = {
    s3.provider_id: s3,
    #azure.provider_id: azure,
}
domain = StorageDomain(secondaryAdaptor, storage_provider_adaptors=storage_provider_adaptors)
primaryAdaptor = SDKStorageAdaptor(domain)