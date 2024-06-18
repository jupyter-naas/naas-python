import pytest
from pydantic import ValidationError

from naas_python.domains.registry.adaptors.primary.TyperRegistryAdaptor import (
    TyperRegistryAdaptor,
)
from naas_python.domains.registry.RegistrySchema import (
    IRegistryDomain,
    Registry,
    RegistryCreationResponse,
    RegistryGetResponse,
    RegistryListResponse,
    RegistryCredentialsResponse,
    RegistryCredentials,
)


@pytest.fixture
def mock_domain():
    # You can create a mock implementation of IRegistryDomain for testing purposes
    class MockRegistryDomain(IRegistryDomain):
        def create(self, name):
            return RegistryCreationResponse(registry=Registry(name=name))

        def list(self, page_size=0, page_number=0):
            return RegistryListResponse(
                registries=[Registry(name=f"Registry-{i}") for i in range(1, 4)]
            )

        def get_registry_by_name(self, name):
            return RegistryGetResponse(registry=Registry(name=name))

        def delete(self, name):
            pass

        def get_credentials(self, name):
            return RegistryCredentialsResponse(
                name=name,
                credentials=RegistryCredentials(
                    username="username",
                    password="password",
                ),
            )

    return MockRegistryDomain()


def test_create_valid_registry(mock_domain, capsys):
    app = TyperRegistryAdaptor(mock_domain)
    app.create("valid-registry-name", rich_preview=False)
    captured = capsys.readouterr()
    assert "valid-registry-name" in captured.out


def test_create_invalid_registry(mock_domain):
    app = TyperRegistryAdaptor(mock_domain)
    with pytest.raises(ValidationError, match="1 validation error for Registry"):
        app.create("invalid_registry_name", rich_preview=False)


def test_create_registry(mock_domain, capsys):
    app = TyperRegistryAdaptor(mock_domain)
    app.create("Test-Registry", rich_preview=False)
    captured = capsys.readouterr()
    assert "Test-Registry" in captured.out


def test_list_registries(mock_domain, capsys):
    app = TyperRegistryAdaptor(mock_domain)
    app.list(rich_preview=False)
    captured = capsys.readouterr()
    assert "Registry-1" in captured.out
    assert "Registry-2" in captured.out
    assert "Registry-3" in captured.out


def test_get_registry(mock_domain, capsys):
    app = TyperRegistryAdaptor(mock_domain)
    app.get("Test-Registry", rich_preview=False)
    captured = capsys.readouterr()
    assert "Test-Registry" in captured.out


def test_delete_registry(mock_domain, capsys):
    app = TyperRegistryAdaptor(mock_domain)
    app.delete("Test-Registry")

    # assert by executing the list command
    app.list(rich_preview=False)
    captured = capsys.readouterr()
    assert "Test-Registry" not in captured.out


def test_get_credentials(mock_domain, capsys):
    app = TyperRegistryAdaptor(mock_domain)
    app.get_credentials("Test-Registry")

    # assert by inspecting name-credentials.txt file
    with open("Test-Registry-credentials.txt", "r") as f:
        contents = f.read()

    assert "Test-Registry" in contents
    assert "username" in contents
    assert "password" in contents

    # remove the file
    import os

    os.remove("Test-Registry-credentials.txt")
