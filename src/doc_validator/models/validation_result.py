"""ValidationResult model for storing results of documentation validation checks."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Severity(Enum):
    """Validation issue severity levels."""
    
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Stores results of documentation validation checks."""
    
    file_path: str
    rule_name: str
    severity: Severity
    line_number: Optional[int]
    message: str
    suggestion: Optional[str]
    validated_at: datetime
    
    def __post_init__(self) -> None:
        """Set validation timestamp if not provided."""
        if not self.validated_at:
            self.validated_at = datetime.now()
    
    @classmethod
    def create_error(cls, file_path: str, rule_name: str, message: str,
                    line_number: Optional[int] = None, suggestion: Optional[str] = None) -> "ValidationResult":
        """Create an error-level validation result."""
        return cls(
            file_path=file_path,
            rule_name=rule_name,
            severity=Severity.ERROR,
            line_number=line_number,
            message=message,
            suggestion=suggestion,
            validated_at=datetime.now()
        )
    
    @classmethod
    def create_warning(cls, file_path: str, rule_name: str, message: str,
                      line_number: Optional[int] = None, suggestion: Optional[str] = None) -> "ValidationResult":
        """Create a warning-level validation result."""
        return cls(
            file_path=file_path,
            rule_name=rule_name,
            severity=Severity.WARNING,
            line_number=line_number,
            message=message,
            suggestion=suggestion,
            validated_at=datetime.now()
        )
    
    @classmethod
    def create_info(cls, file_path: str, rule_name: str, message: str,
                   line_number: Optional[int] = None) -> "ValidationResult":
        """Create an info-level validation result."""
        return cls(
            file_path=file_path,
            rule_name=rule_name,
            severity=Severity.INFO,
            line_number=line_number,
            message=message,
            suggestion=None,
            validated_at=datetime.now()
        )
    
    def format_for_display(self) -> str:
        """Format validation result for human-readable display."""
        severity_symbol = {
            Severity.ERROR: "✗",
            Severity.WARNING: "⚠",
            Severity.INFO: "ℹ"
        }
        
        symbol = severity_symbol.get(self.severity, "•")
        line_info = f" (line {self.line_number})" if self.line_number else ""
        
        result = f"{symbol} {self.file_path}{line_info}: {self.message}"
        
        if self.suggestion:
            result += f"\n  Suggestion: {self.suggestion}"
            
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file": self.file_path,
            "rule": self.rule_name,
            "severity": self.severity.value,
            "line": self.line_number,
            "message": self.message,
            "suggestion": self.suggestion,
            "validated_at": self.validated_at.isoformat()
        }