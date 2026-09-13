from abc import ABC, abstractmethod
from typing import Any


class ToolInterface(ABC):
    """Base interface for tools exposed to other agent modules."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with the supplied parameters."""
        raise NotImplementedError