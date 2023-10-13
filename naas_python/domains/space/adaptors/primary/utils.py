from contextlib import contextmanager
from typing import List

import rich
from pydantic import BaseModel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


class PydanticTableModel:
    def __init__(self, models: List[BaseModel]):
        super().__init__()
        self.models = models
        self.rich_table()

    def rich_table(self):
        # Get the field names from the first model in the list, and remove the resources and protocols fields
        field_names = [
            field
            for field in self.models[0].__fields__.keys()
            if field not in ["resources", "protocols", "id", "user_id", "env"]
        ]

        # Create table and add header
        self.table = Table(*field_names, show_header=True, header_style="bold cyan")

        # Add data rows
        for model in self.models:
            _model = model.dict()
            row_values = [str(_model[field]) for field in field_names]
            self.table.add_row(*row_values)

    def add_models(self):
        for space in self.models:
            pieces = [
                f"{k}: {v}\n"
                for k, v in space.dict().items()
                if k not in ["resources", "protocols", "env"] and v
            ]

            max_length = max([len(piece) for piece in pieces])
            splitter = "-" * max_length
            rich.print(f"{splitter}\n{''.join(pieces)}{splitter}")


class CustomProgress:
    def __init__(self, mode="plain"):
        self.mode = mode
        self.progress = None

    @contextmanager
    def __enter__(self):
        if self.mode == "rich":
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            )
            yield self.progress
        else:

            class PlainProgress:
                def __init__(self):
                    self.task_description = ""

                def add_task(self, description, total):
                    print(description)
                    self.task_description = description

                def update(self, task, description=None, advance=None):
                    if description:
                        self.task_description = description
                    if advance is not None:
                        print(f"{self.task_description} ({advance * 100:.0f}%)")

            self.progress = PlainProgress()
            yield self.progress

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()


# TODO: Remove this function, now replaced by the above class
def update_progress(task, description, advance, mode) -> None:
    """
    Update a progress task based on the specified mode.

    Args:
        task (Task): The progress task to update.
        description (str): The description to set for the task.
        advance (float): The advance value for the task (0.0 to 1.0).
        mode (str): The mode to determine how to update the progress.
            - "plain": Print the description as plain text.
            - "rich": Update the task description with rich progress.

    Returns:
        None
    """
    if mode == "plain":
        print(description)
    else:
        task.update(description=description, advance=advance)
