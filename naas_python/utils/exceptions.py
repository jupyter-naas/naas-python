import os
from os import getenv
import click
from datetime import datetime

import logging


class NaasException(click.ClickException):
    """
    Custom exception class with optional debugging and logging features.

    Attributes:
        original_exception (Exception): The original exception, if any.
        now (datetime): Current timestamp.
        debug (bool): Debug mode flag.
        log_level (int): Custom log level for logging.
    """

    def __init__(
        self, message, original_exception=None, debug=False, log_level=logging.ERROR
    ):
        """
        Initialize the NaasException object.

        Args:
            message (str): The error message.
            original_exception (Exception, optional): The original exception, if any.
            debug (bool, optional): Enable debug mode.
            log_level (int, optional): Custom log level for logging.
        """
        self.original_exception = original_exception
        self.now = datetime.now()
        self.debug = self._validate_debug_mode(debug)
        self.log_level = log_level
        super().__init__(f"[{self._get_class_name()}]: {message}")
        self._handle_debug_mode()

    def _validate_debug_mode(self, debug):
        """
        Load the NAAS_PYTHON_DEBUG environment variable and validate it with the corresponding boolean value.
        """

        debug_mode = getenv("NAAS_PYTHON_DEBUG", debug)

        if isinstance(debug_mode, bool):
            return debug_mode

        elif isinstance(debug_mode, str):
            if debug_mode.capitalize() == "True":
                return True
            elif debug_mode.capitalize() == "False":
                return False
        else:
            raise ValueError(
                f"Invalid value for NAAS_PYTHON_DEBUG environment variable: {debug_mode}"
            )

    def _handle_debug_mode(self):
        """
        Handle debug mode by logging traceback if enabled.
        """
        if self.debug:
            exception_to_log = self.original_exception or self
            self._log_traceback(exception_to_log)

    def _get_class_name(self):
        """
        Get the name of the current class.

        Returns:
            str: The name of the current class.
        """
        return self.__class__.__name__

    def _log_traceback(self, exception):
        """
        Log the traceback of an exception.

        Args:
            exception (Exception): The exception to log the traceback for.
        """
        logger = logging.getLogger(__name__)
        logger.log(self.log_level, "Exception occurred:", exc_info=True)

    def _traceback_filename(self):
        """
        Generate a unique traceback filename.

        Returns:
            str: The unique traceback filename.
        """
        base_filename = f"error_{self.now.strftime('%Y%m%d')}"
        files = [
            f
            for f in os.listdir(".")
            if os.path.isfile(f) and f.startswith(base_filename)
        ]

        if not files:
            return f"{base_filename}.traceback"

        last_file = max(files)
        int_value = int(last_file.split(".")[1]) + 1
        return f"{base_filename}_{int_value}.traceback"
