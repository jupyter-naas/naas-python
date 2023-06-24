from unittest.mock import patch
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
def mock_token_file():
    token_file = Path.home() / ".naas" / "credentials"
    token_file.write_text("NAAS_TOKEN=test_token")
    return token_file


@pytest.fixture
def cli_runner():
    # Fixture to execute CLI commands
    def run_cli_command(command):
        result = os.system(command)
        return result

    return run_cli_command


def test_authorization_callback_with_token(cli_runner):
    token = generate_test_token_hash()
    command = f"naas-python space --token {token} add"

    result = cli_runner(command)

    assert result == 0


def test_authorization_callback_without_token(cli_runner):
    # Set the NAAS_TOKEN environment variable
    os.environ["NAAS_TOKEN"] = generate_test_token_hash()

    command = "naas-python space add"

    result = cli_runner(command)

    assert result == 0


def test_authorization_callback_missing_token(cli_runner):
    # make sure that the NAAS_TOKEN environment variable is not set and that the credentials file does not exist
    if "NAAS_TOKEN" in os.environ:
        del os.environ["NAAS_TOKEN"]

    if (credentials_file := Path.home() / ".naas" / "credentials").exists():
        os.remove(credentials_file)

    command = "naas-python space add"

    result = cli_runner(command)

    assert result != 0


def test_authorization_callback_missing_token_with_file(cli_runner, mock_token_file):
    command = "naas-python space add"

    result = cli_runner(command)

    assert result == 0
