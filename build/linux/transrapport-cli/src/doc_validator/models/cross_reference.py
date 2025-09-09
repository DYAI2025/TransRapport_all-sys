"""CrossReference model for tracking usage of terminology across documentation files."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ReferenceType(Enum):
    """Types of cross-references."""
    
    DEFINITION = "definition"
    USAGE = "usage" 
    LINK = "link"


@dataclass
class CrossReference:
    """Tracks usage of terminology and concepts across documentation files."""
    
    term: str
    source_file: str
    line_number: int
    context: str
    reference_type: ReferenceType
    is_valid: bool
    
    @classmethod
    def create_link_reference(cls, term: str, source_file: str, line_number: int, 
                             context: str, is_valid: bool = True) -> "CrossReference":
        """Create a cross-reference for markdown links."""
        return cls(
            term=term,
            source_file=source_file,
            line_number=line_number,
            context=context,
            reference_type=ReferenceType.LINK,
            is_valid=is_valid
        )
    
    @classmethod
    def create_term_usage(cls, term: str, source_file: str, line_number: int,
                         context: str, is_valid: bool = True) -> "CrossReference":
        """Create a cross-reference for terminology usage."""
        return cls(
            term=term,
            source_file=source_file,
            line_number=line_number,
            context=context,
            reference_type=ReferenceType.USAGE,
            is_valid=is_valid
        )
    
    @classmethod
    def create_definition(cls, term: str, source_file: str, line_number: int,
                         context: str) -> "CrossReference":
        """Create a cross-reference for term definitions."""
        return cls(
            term=term,
            source_file=source_file,
            line_number=line_number,
            context=context,
            reference_type=ReferenceType.DEFINITION,
            is_valid=True  # Definitions are always valid
        )
    
    def get_context_preview(self, max_length: int = 50) -> str:
        """Get a shortened version of the context for display."""
        if len(self.context) <= max_length:
            return self.context
            
        # Try to break at word boundaries
        truncated = self.context[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:  # If we can break reasonably close
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."