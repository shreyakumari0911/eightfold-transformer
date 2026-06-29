from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseParser(ABC):
    """
    Abstract base parser class.
    All source parsers (PDF, CSV, JSON, etc.) must implement the parse method.
    """
    
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Reads a file from the filesystem and extracts raw, unnormalized candidate data.
        Returns a dictionary mapping candidate field names to their raw values.
        """
        pass
