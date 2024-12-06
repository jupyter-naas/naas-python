# 🐍 Naas Python SDK

## Overview

Naas Python SDK is a software development kit that provides interfaces and implementations for interacting with Naas services. The project follows a hexagonal architecture pattern with clear separation between domains, adaptors, and interfaces.

## Key Features
- Space Management: Deploy and manage cloud applications
- Storage Operations: S3-compatible storage with credential management
- Asset Management: Handle digital assets
- Registry Support: Container registry operations
- Secret Management: Secure credential handling
- CI/CD Integration: Automated pipeline generation

## Project Structure

The project is organized into several key components:

### 1. Core Domains

- **Asset Domain**: Handles asset management operations
- **Space Domain**: Manages space-related operations
- **Storage Domain**: Handles storage operations
- **Secret Domain**: Manages secrets and credentials
- **Registry Domain**: Handles registry operations

Each domain follows a similar structure:
```
domains/
  ├── domain_name/
  │   ├── adaptors/
  │   │   ├── primary/
  │   │   └── secondary/
  │   ├── handlers/
  │   ├── models/
  │   ├── DomainSchema.py
  │   └── DomainDomain.py
```

### 2. Architecture

The project implements a hexagonal (ports and adapters) architecture with:

- **Primary Adapters**: Handle incoming requests (CLI, SDK)
- **Secondary Adapters**: Handle outgoing requests (API calls)
- **Domain Logic**: Core business logic
- **Schemas**: Interface definitions using abstract base classes

### 3. Key Components

#### CLI Interface
The project provides a CLI interface through Typer:

```1:9:naas_python/main.py
from naas_python.cli import app


def main():
    app()


if __name__ == "__main__":
    main()
```


#### Storage Provider Support
Includes S3 storage provider implementation with credential management:

```202:249:naas_python/domains/storage/adaptors/secondary/providers/S3StorageProviderAdaptor.py
    def save_naas_credentials(self, workspace_id:str, storage_name:str, credentials:dict)-> str:

        self.naas_bucket = urlparse(credentials['credentials']['s3']['endpoint_url']).netloc
        self.naas_workspace_id = urlparse(credentials['credentials']['s3']['endpoint_url']).path.split('/')[1]
        self.naas_storage = urlparse(credentials['credentials']['s3']['endpoint_url']).path.split('/')[2]
        
        s3_credentials = {
            "provider": "s3",
            "workspace_id": self.naas_workspace_id,
            "storage_name": self.naas_storage,
            "endpoint_url": f"s3.{credentials['credentials']['s3']['region_name']}.amazonaws.com",
            "bucket": f"{self.naas_bucket}",
            "region_name": credentials['credentials']['s3']['region_name'],
            "access_key_id": credentials['credentials']['s3']['access_key_id'],
            "secret_key": credentials['credentials']['s3']['secret_key'],
            "session_token": credentials['credentials']['s3']['session_token'],
            "expiration": credentials['credentials']['s3']['expiration']
        }

        # write the credentials to the file
        naas_credentials = os.path.expanduser(self.naas_credentials)
        existing_data = {}

        if os.path.exists(naas_credentials):
            with open(naas_credentials, 'r') as f:
                existing_data = json.load(f)
        # Ensure 'storage' key exists in existing_data
        if 'storage' not in existing_data:
            existing_data['storage'] = {}

        # Update the 'storage' key with new credentials
        existing_data['storage'].update({
            s3_credentials['workspace_id']: {
                    s3_credentials['storage_name']: {
                        s3_credentials["provider"]: {
                        "REGION_NAME": s3_credentials['region_name'],
                        "AWS_ACCESS_KEY_ID": s3_credentials['access_key_id'],
                        "AWS_SECRET_ACCESS_KEY": s3_credentials['secret_key'],
                        "AWS_SESSION_TOKEN": s3_credentials['session_token'],
                        "AWS_SESSION_EXPIRATION_TOKEN": s3_credentials['expiration']
                    }
                }
            }
        })
        with open(naas_credentials, 'w') as f:
            json.dump(existing_data, f)
        return ("generated s3 credentials.")
```


#### CI/CD Integration
Supports automatic CI/CD configuration generation:

```124:222:naas_python/domains/space/adaptors/primary/SDKSpaceAdaptor.py
        # Step 2.a: Build and push image to registry container if requested:
        if space_type == "docker":
            print(f"Building Docker Image for '{space_name}'...")
            os.system(
                f"docker build -t {registry.registry.uri}:latest -f {dockerfile_path} {docker_context}"
            )

            print("Pushing Docker Image...")
            os.system(f"docker push {registry.registry.uri}:latest")

        # Step 2.b: Create a new space on space.naas.ai
        print(f"Creating Naas Space '{space_name}'...")
        try:
            self.domain.create(
                name=space_name,
                domain=f"{space_name}.naas.ai",
                containers=[
                    {
                        "name": space_name,
                        "image": image if image else f"{registry.registry.uri}:latest",
                        "env": {},
                        "cpu": cpu,
                        "memory": memory,
                        "port": container_port,
                    }
                ],
            )
        except SpaceConflictError as e:
            print(
                f"A space with the name '{space_name}' already exists. Proceeding with existing space."
            )
            self.domain.get(name=space_name)
        # Step 3: Generate CI/CD configuration if requested
        if generate_ci:
            pipeline = Pipeline(name=f"ci-{space_name}")

            # Check for naas_python cli help command
            pipeline.add_job(
                "Validate that naas_python works",
                [
                    "name: Validate that naas_python works",
                    "run: |",
                    "  naas_python --help",
                ],
            )

            # Check Naas Space status
            pipeline.add_job(
                "Check Naas Space status",
                [
                    "name: Check Naas Space status",
                    "run: |",
                    f"  naas_python space get --name { space_name }",
                ],
            )

            # Check Naas Registry status
            pipeline.add_job(
                "Check Naas Registry status",
                [
                    "name: Check Naas Registry status",
                    "run: |",
                    f"  naas_python registry get --name { registry_name }",
                ],
            )

            # Add custom jobs for CI/CD configuration
            if space_type == "docker":
                # Retrieve credentials from registry and login into docker
                pipeline.add_job(
                    "Login to Docker Registry",
                    [
                        "name: Login to Docker Registry",
                        "run: |",
                        f"  naas_python registry docker-login --name { registry_name }",
                    ],
                )

                try:
                    _build_command = f"  docker build -t {registry.registry.uri}:latest -f {dockerfile_path} {docker_context}"
                except ValueError as e:
                    raise ValueError(
                        "When space_type is 'docker', dockerfile_path and docker_context must be provided. Please provide these values and try again"
                    ) from e

                docker_steps = [
                    "name: Build and Push Docker Image",
                    f'if: ${{ github.event_name == "push" }}',
                    "run: |",
                    _build_command,
                    f"  docker push { registry.registry.uri }:latest",
                ]
                pipeline.add_job("Build and Push Docker Image", docker_steps)
            # Render the CI/CD configuration
            pipeline.render()

            print("Generated CI/CD configuration.")
```


## Installation

The project uses Poetry for dependency management:

```1:31:pyproject.toml
[tool.poetry]
name = "naas-python"
version = "0.1.0"
description = "Naas Python SDK"
authors = ["Maxime Jublou <maxime@naas.ai>"]
license = "AGPL"
readme = "README.md"
packages = [{ include = "naas_python" }]

[tool.poetry.dependencies]
python = "^3.9"
typer = { extras = ["all"], version = "^0.9.0" }
requests = "^2.31.0"
cachetools = "^5.3.1"
jinja2 = "^3.0.1"
naas-models = "^1.11.2"
grpcio = "^1.60.0"
pydash = "^7.0.7"
boto3 = "^1.34.128"
pydantic = "<2.9"

[tool.poetry.group.dev.dependencies]
pytest = "^7.3.1"
requests = "^2.31.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.scripts]
naas-python = "naas_python.main:main"
```


To install:
```bash
poetry install
```

## Usage

### As a Library

```python
import naas_python as naas

# Space operations
naas.space.add(space_name="my-space")

# Storage operations
naas.storage.create(workspace_id="123", storage_name="my-storage")

# Asset operations
naas.asset.create(workspace_id="123", asset_creation=asset_data)
```

### Command Line Interface

```bash
naas-python space add --name my-space
naas-python storage create --workspace-id 123 --name my-storage
naas-python asset create --workspace-id 123 --data asset_data.json
```

## Development

### Testing

Tests are written using pytest:

```1:18:tests/test_lib.py
import pytest


def test_lib_add_import():
    import naas_python as naas

    # Test if ``naas.space.add`` is a valid method and callable

    assert callable(naas.space.add)


def test_missing_keys_call():
    import naas_python as naas

    # Test if ``naas.space.add`` is a valid method and callable

    with pytest.raises(TypeError):
        naas.space.add()
```


Run tests with:
```bash
make test
```

### Git Hooks

The project includes pre-commit hooks for running tests:

```1:17:.github/hooks/pre-commit
#!/bin/sh

# Execute the make target
make test

# Capture the exit status of the make command
STATUS=$?

# If the make command fails, exit with the same status
if [ $STATUS -ne 0 ]; then
    echo "Pre-commit hook failed: make test failed with status $STATUS"
    exit $STATUS
fi

# If the make command succeeds, allow the commit to proceed
exit 0

```


## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0):


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (`make test`)
5. Submit a pull request

The project uses semantic release for versioning:

```1:37:.github/workflows/release.yml
name: Release
on:
  push:
    branches:
      - main
      - dev

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2
        with:
          fetch-depth: 0
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 'lts/*'
      - name: Install dependencies
        run: |
          cd .github \
            && npm ci \
            && cd .. \
            && (rm package.json || true) \
            && (rm package-lock.json || true) \
            && ln -s .github/node_modules node_modules \
            && ln -s .github/package.json package.json \
            && ln -s .github/package-lock.json package-lock.json \
            && ln -s .github/.releaserc .releaserc
      - name: Release
        env:
#          GITHUB_TOKEN: ${{ secrets.ACCESS_TOKEN }} # Use this if you need to trigger CI/CD based on new release being published.
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: npx semantic-release
```


## Error Handling

The project implements custom exceptions for different error scenarios:

```9:11:naas_python/domains/asset/AssetSchema.py
class AssetNotFound(NaasException): pass
class AssetConflictError(NaasException): pass
class AssetRequestError(NaasException): pass
```
