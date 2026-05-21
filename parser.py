from pathlib import Path
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class Loader:
    def load_file(self, file_path: str) -> Any:
        """
        Loads a configuration file.
        Handles cases: missing file, empty file, permission error
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Missing file: '{path.name}' not found")

        if not path.is_file():
            raise ValueError(f"'{file_path}' is not a regular file")

        try:
            with open(path, mode="r", encoding="utf-8") as f:
                content = f.read().strip()
        except PermissionError:
            raise PermissionError(
                f"You don't have permission for the directory '{path.parent}'"
                f"or for the file'{path.name}'"
            )

        if not content:
            raise ValueError(f"file '{path.name} is empty.")

        return (content)

class Parameters(BaseModel):
    nb_drones: int = Field(..., ge=1)
    start_hub: list[str, int, int] = Field(...)
    end_hub: list[str, int, int] = Field(...)
    hub: list[str, int, int] = Field(...)
    connection: str = Field(min_length=1)



