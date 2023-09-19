import logging
import os
from datetime import datetime
from pathlib import Path

from rich.logging import RichHandler


def initialize_logging(logging_dir: Path = None, persistent_max: int = 3):
    # Create a logger
    logger = logging.getLogger("naas_python")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        # The logger already has handlers attached to it
        return logger

    # Create a rich handler
    rich_handler = RichHandler(level=logging.INFO)

    # Add the rich handler to the logger
    logger.addHandler(rich_handler)

    # Create a file handler if a logging directory is specified
    if logging_dir is None:
        logging_dir = os.environ.get("NAAS_PYTHON_LOGGING_DIR", Path.cwd() / ".logs")
    logging_dir.mkdir(parents=True, exist_ok=True)

    filename = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    file_handler = logging.FileHandler(filename=logging_dir / filename)
    file_handler.setLevel(logging.DEBUG)

    # Update the formatter
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Remove precedent log files
    _remove_precedent_log_files(log_dir=logging_dir, lof_max=persistent_max)

    return logger


def _remove_precedent_log_files(log_dir: Path, lof_max: int = 3):
    # Remove precedent log files if they exceed the maximum allowed
    log_files = list(log_dir.glob("*.log"))

    if len(log_files) > lof_max:
        log_files.sort(key=os.path.getmtime)
        for i in range(len(log_files) - lof_max):
            log_file = log_files[i]
            if log_file.exists():
                try:
                    log_file.unlink()  # Remove the file
                except Exception as e:
                    logging.error(f"Failed to remove log file {log_file}: {e}")
