from ..adaptors.secondary.NaasStorageAPIAdaptor import NaasStorageAPIAdaptor
from naas_python.domains.storage.adaptors.secondary.providers.S3StorageProviderAdaptor import S3StorageProviderAdaptor
from ..StorageDomain import StorageDomain
from ..adaptors.primary.TyperStorageAdaptor import TyperStorageAdaptor

import logging

logging.debug("CliStorageHandler.py : Initializing secondaryAdaptor")
secondaryAdaptor = NaasStorageAPIAdaptor()

# du coup peu importe le provider utilisé on charge tout ?
#TODO le sdk
s3 = S3StorageProviderAdaptor()
#azure = AzureStorageProviderAdaptor()

storage_provider_adaptors = {
    s3.provider_id: s3,
    #azure.provider_id: azure,
}

logging.debug("CliStorageHandler.py : Initializing domain")
domain = StorageDomain(secondaryAdaptor, storage_provider_adaptors=storage_provider_adaptors)

logging.debug("CliStorageHandler.py : Initializing primaryAdaptor")
primaryAdaptor = TyperStorageAdaptor(domain)