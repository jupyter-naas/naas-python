import pytest
import os
from pathlib import Path


def generate_test_token_hash():
    import hashlib
    import random
    import string

    random_string = "".join(random.choice(string.ascii_letters) for i in range(10))
    return hashlib.sha256(random_string.encode()).hexdigest()


@pytest.fixture
def sdk_space_adaptor():
    # Create an instance of SDKSpaceAdaptor with a mock domain object
    from naas_python.domains.space.adaptors.secondary.NaasSpaceAPIAdaptor import (
        NaasSpaceAPIAdaptor,
    )
    from naas_python.domains.space.SpaceDomain import SpaceDomain
    from naas_python.domains.space.adaptors.primary.SDKSpaceAdaptor import (
        SDKSpaceAdaptor,
    )

    secondaryAdaptor = NaasSpaceAPIAdaptor()
    domain = SpaceDomain(secondaryAdaptor)
    return SDKSpaceAdaptor(domain)


def test_credentials_with_token(sdk_space_adaptor):
    # Set a token for credentials
    _token = generate_test_token_hash()

    # Call the credentials method
    credentials = sdk_space_adaptor.credentials(token=_token)

    # Verify that credentials.token matches the provided token
    assert credentials.token == _token


def test_credentials_without_token(sdk_space_adaptor):
    # validation token
    _token = generate_test_token_hash()

    # Set the NAAS_TOKEN environment variable
    os.environ["NAAS_TOKEN"] = _token

    # Call the credentials method without providing a token
    credentials = sdk_space_adaptor.credentials()

    # Verify that credentials.token matches the environment variable value
    assert credentials.token == _token

    # Clean up the environment variable
    del os.environ["NAAS_TOKEN"]


def test_credentials_missing_token(sdk_space_adaptor):
    # make sure that the NAAS_TOKEN environment variable is not set and that the credentials file does not exist
    if "NAAS_TOKEN" in os.environ:
        del os.environ["NAAS_TOKEN"]

    if (credentials_file := Path.home() / ".naas" / "credentials").exists():
        os.remove(credentials_file)

    # Call the credentials method without a token or credentials file
    with pytest.raises(Exception):
        sdk_space_adaptor.credentials()
