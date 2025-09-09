"""DocumentationFile model for representing documentation files with metadata."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional
import hashlib


class ValidationStatus(Enum):
    """Validation status enumeration."""
    
    VALID = "valid"
    INVALID = "invalid"
    NOT_VALIDATED = "not_validated"


@dataclass
class DocumentationFile:
    """Represents each of the four core documentation files with metadata and validation state."""
    
    path: Path
    name: str
    version: str
    size_bytes: int
    last_validated: Optional[datetime]
    validation_status: ValidationStatus
    dependencies: List[str]
    
    @classmethod
    def from_path(cls, file_path: Path) -> "DocumentationFile":
        """Create DocumentationFile from file path."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Calculate file hash as version
        content = file_path.read_text(encoding='utf-8')
        version = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Extract name from path
        name = file_path.stem.lower()
        if "transrapport" in name:
            name = "transrapport"
        elif "architecture" in name:
            name = "architecture"
        elif "terminologie" in name:
            name = "terminologie"
        elif "marker" in name:
            name = "marker"
            
        return cls(
            path=file_path,
            name=name,
            version=version,
            size_bytes=file_path.stat().st_size,
            last_validated=None,
            validation_status=ValidationStatus.NOT_VALIDATED,
            dependencies=[]
        )
    
    def update_validation_status(self, status: ValidationStatus) -> None:
        """Update validation status and timestamp."""
        self.validation_status = status
        self.last_validated = datetime.now()
    
    def needs_revalidation(self) -> bool:
        """Check if file needs revalidation based on modification time."""
        if self.last_validated is None:
            return True
            
        file_mtime = datetime.fromtimestamp(self.path.stat().st_mtime)
        return file_mtime > self.last_validated