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

    def create(self, name: str, value: str) -> None:
        response = self.adaptor.create_secret(
            name=name, value=value,
        )
        return response

    def bulk_create(self, secrets_list: List[Secret]) -> None:
        response = self.adaptor.bulk_create(
            secrets_list=secrets_list
        )

    def get(self, name: str) -> Secret:
        response = self.adaptor.get_secret(name=name)
        return response

    def delete(self, name: str) -> None:
        return self.adaptor.delete_secret(name=name)

    def list(self, page_size: int, page_number: int) -> List[Secret]:
        secrets = self.adaptor.list_secrets(
            page_size=page_size, page_number=page_number
        )
        return secrets
