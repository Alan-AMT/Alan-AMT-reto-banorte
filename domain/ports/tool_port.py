from abc import ABC, abstractmethod
from typing import Any, Dict


class ToolPort(ABC):
    name: str
    description: str
    args_schema: Dict[str, Any]

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        """
        Execute the tool with the given keyword arguments.
        
        Returns:
            The output/result of the tool execution.
        """
        pass
