import os

from rich.panel import Panel
from rich import print as rprint

from naas_python.domains.secret.SecretSchema import (
    ISecretDomain,
    ISecretInvoker,
    SecretCreateResponse,
    SecretGetResponse,
    SecretListResponse,
    SecretDeleteResponse
)

class SDKSecretAdaptor(ISecretInvoker):
    domain: ISecretDomain

    def __init__(self, domain: ISecretDomain):
        self.domain = domain

    def create(self, name: str = "", value: str ="") -> SecretCreateResponse:
        """Create a secret with the given name"""
        secret = self.domain.create(name=name, value=value)
        return secret

    def list(self, page_size: int = 0, page_number: int = 0) -> SecretListResponse:
        """List all secrets for the current user"""
        secret_list = self.domain.list(page_size=page_size, page_number=page_number)
        return secret_list

    def get(self, name="") -> SecretGetResponse:
        """Get a secret with the given name"""
        secret = self.domain.get(name=name)
        return secret

    def delete(self, name="") -> SecretDeleteResponse:
        """Delete a secret by name"""
        secret = self.domain.delete(name=name)
        return secret
