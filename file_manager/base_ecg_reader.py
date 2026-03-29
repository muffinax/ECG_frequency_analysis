from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .file_manager import FileManager


class BaseECGReader(ABC):

    @abstractmethod
    def read(self, filepath: str, file_manager: "FileManager") -> None:
        pass
