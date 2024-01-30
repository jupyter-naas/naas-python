from typing import List
from .models.Secret import Secret

from typing import List

from naas_python.domains.secret.SecretSchema import (
    ISecretDomain,
    ISecretAdaptor,
    Secret,
    SecretListResponse,
    SecretResponseError,
    SecretError,
    SecretCreateResponse,
    SecretCreateRequest,
    # SecretCredentialsResponse,
    # SecretAdd
)
class SecretDomain(ISecretDomain):
    def __init__(self, adaptor: ISecretAdaptor):
        self.adaptor = adaptor

    def create(self, name: str, value: str) -> Secret:
        response = self.adaptor.create_secret(
            name=name, value=value,
        )
        # return Secret(**response)
        return response

    def get(self, name: str):
        response = self.adaptor.get(name=name)
        return response

    def delete(self, name: str):
        return self.adaptor.delete_secret(name=name)

    def list(self, page_size: int, page_number: int) -> List[Secret]:
    # def list(self, page_size: int, page_number: int) -> List[str]:
        secrets = self.adaptor.list_secrets(
            page_size=page_size, page_number=page_number
        )
        return secrets

        # print(f"response:{[response[0]['secret']]}
        # return SecretListResponse(secrets=(response), error=SecretResponseError(error=0, message="Sucess"))        
        # return SecretListResponse(secrets=(response[0]['secrets']), error=SecretResponseError(error=0, message="Sucess"))
        # print(f"{self.adaptor.list_secrets}response:[response[0]['secret']")
        # return SecretListResponse((response[0]['secrets']), error=SecretResponseError(error=0, message="Sucess"))
    
    # def update(self, name: str, containers: list, domain: str) -> Secret:
    #     response = self.adaptor.update_secret(
    #         name=name, containers=containers, domain=domain
    #     )
    #     return Secret(**response)
