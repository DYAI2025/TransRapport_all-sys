"""TerminologyEntry model for representing definitions with usage tracking."""
from dataclasses import dataclass
from typing import List
import re


@dataclass
class TerminologyEntry:
    """Represents definitions from terminologie.md with usage tracking across documents."""
    
    term: str
    definition: str
    aliases: List[str]
    category: str
    usage_pattern: str
    
    def __post_init__(self) -> None:
        """Generate usage pattern after initialization."""
        if not self.usage_pattern:
            self.usage_pattern = self._generate_usage_pattern()
    
    def _generate_usage_pattern(self) -> str:
        """Generate regex pattern for finding term usage."""
        # Escape special regex characters in term
        escaped_term = re.escape(self.term)
        
        # Create pattern that matches the term with word boundaries
        # Include variations with underscores and common separators
        patterns = [escaped_term]
        
        # Add aliases to pattern
        for alias in self.aliases:
            patterns.append(re.escape(alias))
        
        # Join with OR operator, add word boundaries
        pattern = r'\b(?:' + '|'.join(patterns) + r')\b'
        
        return pattern
    
    def matches_text(self, text: str) -> List[tuple]:
        """Find all matches of this term in given text."""
        pattern = re.compile(self.usage_pattern, re.IGNORECASE)
        matches = []
        
        for match in pattern.finditer(text):
            matches.append((match.start(), match.end(), match.group()))
            
        return matches
    
    @classmethod
    def create_marker_term(cls, term: str, definition: str) -> "TerminologyEntry":
        """Create a terminology entry for marker levels (ATO, SEM, CLU, MEMA)."""
        aliases = []
        
        # Add common aliases based on term type
        if term == "ATO":
            aliases = ["Atomic Marker", "ATO_", "atomic marker"]
        elif term == "SEM":
            aliases = ["Semantic Marker", "SEM_", "semantic marker"]
        elif term == "CLU":
            aliases = ["Cluster Marker", "CLU_", "cluster marker"]
        elif term == "MEMA":
            aliases = ["Meta Marker", "MEMA_", "meta marker"]
            
        return cls(
            term=term,
            definition=definition,
            aliases=aliases,
            category="marker_level",
            usage_pattern=""
        )
    
    @classmethod
    def create_cli_term(cls, term: str, definition: str) -> "TerminologyEntry":
        """Create a terminology entry for CLI commands."""
        return cls(
            term=term,
            definition=definition,
            aliases=[],
            category="cli_command",
            usage_pattern=""
        )