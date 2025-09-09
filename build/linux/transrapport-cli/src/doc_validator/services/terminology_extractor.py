"""TerminologyExtractor service for extracting terminology from terminologie.md."""
from pathlib import Path
from typing import List
import re

from ..models.terminology_entry import TerminologyEntry


class TerminologyExtractor:
    """Service for extracting terminology definitions from terminologie.md."""
    
    def extract_from_file(self, file_path: Path) -> List[TerminologyEntry]:
        """Extract terminology entries from a terminologie.md file."""
        if not file_path.exists():
            return []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return self._parse_terminology_content(content)
        except Exception:
            return []
    
    def _parse_terminology_content(self, content: str) -> List[TerminologyEntry]:
        """Parse content and extract terminology entries."""
        terms = []
        
        # Extract marker level terminology (ATO, SEM, CLU, MEMA)
        marker_terms = self._extract_marker_terminology(content)
        terms.extend(marker_terms)
        
        # Extract CLI command terminology
        cli_terms = self._extract_cli_terminology(content)
        terms.extend(cli_terms)
        
        # Extract general terminology from headers
        general_terms = self._extract_general_terminology(content)
        terms.extend(general_terms)
        
        return terms
    
    def _extract_marker_terminology(self, content: str) -> List[TerminologyEntry]:
        """Extract marker level terminology (ATO, SEM, CLU, MEMA)."""
        terms = []
        
        # Pattern to match marker definitions
        # Looks for: **ATO_ (Atomic Marker)** · definition text
        marker_pattern = r'\*\*([A-Z]+_?)\s*(?:\(([^)]+)\))?\*\*\s*[·•]\s*([^.\n]+(?:\.[^.\n]*)*)'
        
        matches = re.findall(marker_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            term_name = match[0].rstrip('_')  # Remove trailing underscore
            full_name = match[1] if match[1] else ""
            definition = match[2].strip()
            
            # Skip if not a recognized marker type
            if term_name not in ['ATO', 'SEM', 'CLU', 'MEMA']:
                continue
            
            # Clean up definition
            definition = re.sub(r'\s+', ' ', definition)
            definition = definition.strip('.,;')
            
            # Create aliases
            aliases = []
            if full_name:
                aliases.append(full_name)
            aliases.append(f"{term_name}_")
            
            term = TerminologyEntry(
                term=term_name,
                definition=definition,
                aliases=aliases,
                category="marker_level",
                usage_pattern=""
            )
            
            terms.append(term)
        
        return terms
    
    def _extract_cli_terminology(self, content: str) -> List[TerminologyEntry]:
        """Extract CLI command terminology."""
        terms = []
        
        # Pattern to match CLI commands
        # Looks for: ### me command name or `me command name`
        cli_patterns = [
            r'###\s+(me\s+[^#\n]+)',  # Header format
            r'`(me\s+[^`]+)`',        # Code format
        ]
        
        for pattern in cli_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            for match in matches:
                command = match.strip()
                
                # Extract definition from surrounding context
                definition = self._extract_command_definition(content, command)
                
                term = TerminologyEntry(
                    term=command,
                    definition=definition,
                    aliases=[],
                    category="cli_command",
                    usage_pattern=""
                )
                
                terms.append(term)
        
        return terms
    
    def _extract_general_terminology(self, content: str) -> List[TerminologyEntry]:
        """Extract general terminology from headers."""
        terms = []
        
        # Pattern to match header definitions
        # ## Term Name
        # Definition content
        header_pattern = r'^##\s+([^#\n]+)\n((?:(?!^##).+\n?)*)'
        
        matches = re.findall(header_pattern, content, re.MULTILINE)
        
        for match in matches:
            term_name = match[0].strip()
            definition_content = match[1].strip()
            
            # Skip if it's a section header rather than a term
            if len(term_name.split()) > 4:  # Too long to be a term
                continue
            
            # Clean up definition
            definition = re.sub(r'\s+', ' ', definition_content)
            definition = definition[:200] + "..." if len(definition) > 200 else definition
            
            # Extract aliases from parentheses
            aliases = []
            alias_match = re.search(r'\(([^)]+)\)', term_name)
            if alias_match:
                aliases.append(alias_match.group(1))
            
            term = TerminologyEntry(
                term=term_name,
                definition=definition,
                aliases=aliases,
                category="general",
                usage_pattern=""
            )
            
            terms.append(term)
        
        return terms
    
    def _extract_command_definition(self, content: str, command: str) -> str:
        """Extract definition for a CLI command from surrounding context."""
        # Find the command in content and extract nearby text as definition
        command_pattern = re.escape(command)
        
        # Look for the command and get the line it's on plus next few lines
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if re.search(command_pattern, line, re.IGNORECASE):
                # Collect definition from current and next few lines
                definition_lines = []
                
                # Look for description in next few lines
                for j in range(i + 1, min(i + 4, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        definition_lines.append(lines[j].strip())
                    elif definition_lines:  # Stop at next section
                        break
                
                if definition_lines:
                    definition = ' '.join(definition_lines)
                    return re.sub(r'\s+', ' ', definition)[:150]
        
        return f"CLI command: {command}"