import os
from typing import Any, Type

from crewai.tools import BaseTool
from distutils.util import strtobool
from pydantic import BaseModel


class FileWriterToolInput(BaseModel):
    absolute_path: str
    overwrite: str = "False"
    content: str


class CustomFileWriterTool(BaseTool):
    name: str = "File Writer Tool"
    description: str = (
        "A tool to write content to a specified file. Accepts absolute_path (containing filename), content, and optionally an overwrite flag as input."
    )
    prefix: str = None
    args_schema: Type[BaseModel] = FileWriterToolInput

    def __init__(self, prefix: str = None, *args, **kwargs):
        if prefix is not None:
            kwargs['description'] = f"A tool to write content to a specified file. Accepts absolute_path (containing filename), content, and optionally an overwrite flag as input.\n\nThe filename will be prefixed with: {prefix}"

        super().__init__(*args, **kwargs)
        self.prefix = prefix

    def _run(self, **kwargs: Any) -> str:
        try:
            # Create the directory if it doesn't exist
            # Construct the full path

            filepath = kwargs["absolute_path"]
            if self.prefix:
                file_parts = filepath.split("/")
                file_parts[-1] = f"{self.prefix}_{file_parts[-1]}"
                filepath = "/".join(file_parts)

            # Convert overwrite to boolean
            kwargs["overwrite"] = bool(strtobool(kwargs["overwrite"]))

            # Check if file exists and overwrite is not allowed
            if os.path.exists(filepath) and not kwargs["overwrite"]:
                return f"File {filepath} already exists and overwrite option was not passed."

            # Create directory structure if it doesn't exist
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # Write content to the file
            mode = "w" if kwargs["overwrite"] else "x"
            with open(filepath, mode) as file:
                file.write(kwargs["content"])
            
            return f"Content successfully written to {filepath}"
        except FileExistsError:
            return f"File {filepath} already exists and overwrite option was not passed."
        except KeyError as e:
            return f"An error occurred while accessing key: {str(e)}"
        except Exception as e:
            return f"An error occurred while writing to the file: {str(e)}"
