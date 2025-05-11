import os
from collections import defaultdict
from typing import Any, List, Optional, Type

from crewai.tools import BaseTool
from crewai_tools.tools.directory_read_tool.directory_read_tool import (
    DirectoryReadToolSchema,
    FixedDirectoryReadToolSchema,
)
from pydantic import BaseModel


class CustomDirectoryReadTool(BaseTool):
    name: str = "List files in directory"
    description: str = "A tool that can be used to recursively list a directory's content."
    args_schema: Type[BaseModel] = DirectoryReadToolSchema
    directory: Optional[str] = None
    ignored_dirs: Optional[List[str]] = None

    def __init__(
        self,
        directory: Optional[str] = None,
        ignored_dirs: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if directory is not None:
            self.directory = directory
            self.description = f"A tool that can be used to list {directory}'s content."
            self.args_schema = FixedDirectoryReadToolSchema
            self._generate_description()

        if ignored_dirs is not None:
            self.ignored_dirs = ignored_dirs
        else:
            self.ignored_dirs = []

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        directory = kwargs.get("directory", self.directory)
        if directory[-1] == "/":
            directory = directory[:-1]

        # Group files by directory
        dir_files = defaultdict(list)

        for root, dirs, files in os.walk(directory):
            # Skip ignored directories
            if self.ignored_dirs and any(ignored_dir in root for ignored_dir in self.ignored_dirs):
                continue

            # Get relative directory path
            rel_dir = os.path.relpath(root, directory)
            if rel_dir == ".":
                rel_dir = "/"
            else:
                rel_dir = "/" + rel_dir

            # Add files to this directory
            for filename in files:
                dir_files[rel_dir].append(filename)

        # Sort directories and files for readability
        result = f"Files grouped by directory (relative to {directory}):\n"

        for dir_path in sorted(dir_files.keys()):
            files = sorted(dir_files[dir_path])
            result += f"\n{dir_path}: {files}\n"

        if not dir_files:
            result = f"No files found in {directory}."

        return result
