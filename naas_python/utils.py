import logging
import os
from datetime import datetime
from pathlib import Path

import jinja2
from rich.logging import RichHandler
from rich.theme import Theme


class CLILogger:
    custom_theme = Theme(
        {"info": "dim cyan", "warning": "magenta", "danger": "bold red"}
    )

    def __init__(self, logger_name="NaasPython", log_file: Path = None):
        self.log_file = self._set_log_file(log_file)
        self.logger = self.setup_logger(logger_name)

    def __repr__(self) -> str:
        return f"NaasLogger({self.logger.name})"

    def _remove_precedent_log_files(self, lof_max: int = 3):
        # Remove precedent log files
        log_files = list(Path(__name__).parent.glob("*.log"))
        if len(log_files) > lof_max:
            log_files.sort(key=os.path.getmtime)  # Sort log files by modification time
            for i in range(len(log_files) - lof_max):
                log_file = log_files[i]
                if log_file.exists():
                    os.remove(log_file.absolute().as_posix())

    def _set_log_file(self, log_file: Path):
        log_base_name = "NaasPython"
        if not log_file:
            self._remove_precedent_log_files()
            _now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            return Path(__name__).parent / f".NaasPython-{_now}.log"
        elif not isinstance(log_file, Path):
            raise TypeError(
                "log_file must be a pathlib.Path object not {type(log_file)}"
            )
        elif not log_file.parent.exists():
            raise FileNotFoundError(
                f"{log_file.parent.absolute().as_posix()} does not exist"
            )
        else:
            return log_file

    def setup_logger(self, logger_name):
        # Set up logging

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        # Create a file handler
        file_handler = logging.FileHandler(filename=self.log_file.as_posix())
        file_handler.setLevel(logging.DEBUG)

        # Create a rich handler
        rich_handler = RichHandler()
        rich_handler.setLevel(logging.INFO)
        rich_handler.console.theme = self.custom_theme

        # Create a formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )

        # Set the formatter for the file handler
        file_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(rich_handler)

        return logger

    def _remove_handlers(self):
        # remove handlers from logger, only used for testing
        while len(self.logger.handlers) > 0:
            self.logger.removeHandler(self.logger.handlers[0])


# Update authentication with JupyterHub token structure and the temp create use and password,
# and the space_url. Update user spaces using the python API


def render_cicd_jinja_template(
    dockerfile_path: str,
    docker_context: str,
    registry_name: str,
    space_name: str,
):
    # Define the Jinja2 template for the GitHub Action YAML
    template_str = """
    name: {{ space_name }} CI/CD

    on:
      push:
          tags:
          - '*'

    jobs:
        build:
            runs-on: ubuntu-latest

            steps:
            - name: Checkout code
              uses: actions/checkout@v2

            - name: Authenticate on auth.naas.ai
              run: echo "::set-env name=NAAS_AUTH_TOKEN::<token>"

            - name: Get temporary credentials for registry
              run: echo "Temporary credentials for registry"

            - name: Docker Login
              uses: docker/login-action@v2
              with:
                  registry: space.naas.ai/{{ registry_name }}
                  username: "{{ registry_name }}"
                  password: "{{ registry_password }}"

            - name: Get space URL
              run: |
                  space_url=$(curl -H "Authorization: Bearer $naas_auth_token" https://space.naas.ai/registry/{{ registry_name }} | jq -r .url)

            - name: Build and push Docker container
              run: docker build -f {{ dockerfile_path }} -t $space_url/{{ docker_context }}:latest {{ docker_context }} && docker push $space_url/{{ docker_context }}:latest

            - name: Build and push Docker container
              uses: docker/build-push-action@v2
              with:
                  context: {{ docker_context }}
                  tags: $space_url/{{ docker_context }}::$GITHUB_REF_NAME
                  push: true

            - name: Update space version
              run: echo "Update space image"
    """

    # Create a Jinja2 environment
    env = jinja2.Environment(loader=jinja2.BaseLoader())

    # Load the template
    template = env.from_string(template_str)

    # Render the template with the provided variables
    rendered_template = template.render(
        space_name=space_name,
        registry_name=registry_name,
        dockerfile_path=dockerfile_path,
        docker_context=docker_context,
    )

    return rendered_template
