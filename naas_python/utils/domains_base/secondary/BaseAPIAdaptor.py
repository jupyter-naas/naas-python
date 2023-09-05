import os
from logging import getLogger
import sys
from typing import Any, Literal, Union

import requests
from urllib3.exceptions import NewConnectionError, MaxRetryError
import requests_cache
from requests.exceptions import ConnectionError
from rich.console import Console
from rich.panel import Panel

logger = getLogger(__name__)


class APIAdaptorError(Exception):
    def __init__(self, message, source=None):
        self.message = message
        self.source = source
        super().__init__(self.message)

    def __str__(self):
        return self.message

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        logger.debug(f"{self.__class__.__name__}: {self.message}")
        return super().__call__(*args, **kwds)

    def pretty_print(self):
        console = Console()
        panel = Panel(
            self.message,
            title=f"Error  [{self.__class__.__name__}]",
            title_align="left",
            border_style="bold red",
        )
        console.print(panel)


class BaseAPIAdaptor:
    host = os.environ.get("NAAS_PYTHON_API_BASE_URL", "http://localhost:8000")
    # Cache name is the name of the calling module
    cache_name = __name__
    cache_expire_after = 60  # Cache expires after 60 seconds

    def __init__(self) -> None:
        super().__init__()
        self.logger = getLogger(__name__)
        self.logger.debug(f"API Base URL: {self.host}")
        self.cache_name = __name__
        self._cache_dir_path = None
        self._initialize_cache()

    def _cache_path(self):
        if self._cache_dir_path:
            return self._cache_dir_path
        else:
            os.makedirs(".cache", exist_ok=True)
            self._cache_dir_path = os.path.join(
                ".cache", f"{self.cache_name}_cache.sqlite"
            )
            return self._cache_dir_path

    def _initialize_cache(self):
        # Initialize the requests-cache with a specified cache name and expiration time
        self.logger.debug("Using requests_cache to speed up local tests execution.")

        requests_cache.install_cache(
            cache_name=self._cache_path(),
            expire_after=self.cache_expire_after,
            allowable_methods=("GET", "POST"),
            backend="sqlite",
        )

        self.logger.debug(f"Cache path: {self._cache_dir_path}")
        self.logger.debug(f"Cache expiration time: {self.cache_expire_after} seconds")

    def _check_service_status(self):
        """
        Check the status of the service API before executing other methods.
        """
        try:
            api_response = requests.get(f"{self.host}")

            if api_response.status_code == 200:
                self.logger.debug("Service status: Available")
                return True  # Service is available

            self.logger.debug("Service status: Unavailable")
            return False  # Service is not available

        except (ConnectionError, NewConnectionError, MaxRetryError) as e:
            raise APIAdaptorError(
                f"Unable to connect to [cyan]{self.host}[/cyan]. The service is currently unavailable. Please try again within a few minutes.",
            ) from e

    @staticmethod
    def service_status_decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                self._check_service_status()
                return func(self, *args, **kwargs)
            except APIAdaptorError as e:
                e.pretty_print()
                sys.exit(1)
            except Exception as e:
                raise APIAdaptorError(e) from e

        return wrapper

    def make_api_request(
        self,
        method: Union[
            requests.get, requests.post, requests.patch, requests.put, requests.delete
        ],
        url,
        token=None,
        payload=None,
        headers: dict = {},
    ):
        # Will be updated using the new authorization validators
        if token:
            headers = {"Authorization": f"Bearer {token}"}
        # Status checks will be handled separately
        return method(url, json=payload, headers=headers)
