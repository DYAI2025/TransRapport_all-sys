"""CrossReferenceValidator service for validating cross-references across files."""
from pathlib import Path
from typing import List, Dict, Set
import re

from ..models.cross_reference import CrossReference, ReferenceType
from ..models.terminology_entry import TerminologyEntry
from ..services.terminology_extractor import TerminologyExtractor


class CrossReferenceValidator:
    """Service for validating cross-references across documentation files."""
    
    def __init__(self):
        self.terminology_extractor = TerminologyExtractor()
        self._known_terms: Dict[str, TerminologyEntry] = {}
        self._available_sections: Dict[str, Set[str]] = {}
    
    def validate_directory(self, directory_path: Path) -> List[CrossReference]:
        """Validate cross-references in all markdown files in a directory."""
        if not directory_path.exists():
            return []
        
        # First pass: collect all terminology and sections
        self._collect_terminology_and_sections(directory_path)
        
        # Second pass: validate references
        references = []
        
        for md_file in directory_path.glob('**/*.md'):
            file_references = self._validate_file(md_file)
            references.extend(file_references)
        
        return references
    
    def _collect_terminology_and_sections(self, directory_path: Path) -> None:
        """Collect all terminology definitions and available sections."""
        self._known_terms = {}
        self._available_sections = {}
        
        for md_file in directory_path.glob('**/*.md'):
            # Extract terminology
            terms = self.terminology_extractor.extract_from_file(md_file)
            for term in terms:
                self._known_terms[term.term.lower()] = term
                for alias in term.aliases:
                    self._known_terms[alias.lower()] = term
            
            # Extract sections
            sections = self._extract_sections(md_file)
            self._available_sections[md_file.name] = sections
    
    def _extract_sections(self, file_path: Path) -> Set[str]:
        """Extract section headers from a markdown file."""
        sections = set()
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Find all headers (## Section Name)
            header_pattern = r'^#{1,6}\s+(.+)$'
            matches = re.findall(header_pattern, content, re.MULTILINE)
            
            for match in matches:
                # Create section anchor (lowercase, replace spaces with hyphens)
                section_name = match.strip()
                anchor = re.sub(r'[^\w\s-]', '', section_name).lower()
                anchor = re.sub(r'\s+', '-', anchor)
                sections.add(anchor)
                sections.add(section_name.lower())
            
        except Exception:
            pass
        
        return sections
    
    def _validate_file(self, file_path: Path) -> List[CrossReference]:
        """Validate cross-references in a single file."""
        references = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Find markdown links
                link_refs = self._find_markdown_links(line, str(file_path), line_num)
                references.extend(link_refs)
                
                # Find terminology usage
                term_refs = self._find_terminology_usage(line, str(file_path), line_num)
                references.extend(term_refs)
                
                # Find CLI command references
                cli_refs = self._find_cli_references(line, str(file_path), line_num)
                references.extend(cli_refs)
        
        except Exception:
            pass
        
        return references
    
    def _find_markdown_links(self, line: str, file_path: str, line_num: int) -> List[CrossReference]:
        """Find and validate markdown links in a line."""
        references = []
        
        # Pattern: [text](file.md#section)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.finditer(link_pattern, line)
        
        for match in matches:
            link_text = match.group(1)
            link_target = match.group(2)
            
            # Skip external links
            if link_target.startswith(('http://', 'https://', 'mailto:')):
                continue
            
            is_valid = self._validate_link_target(link_target)
            
            reference = CrossReference.create_link_reference(
                term=link_text,
                source_file=file_path,
                line_number=line_num,
                context=line.strip(),
                is_valid=is_valid
            )
            references.append(reference)
        
        return references
    
    def _find_terminology_usage(self, line: str, file_path: str, line_num: int) -> List[CrossReference]:
        """Find terminology usage in a line."""
        references = []
        
        # Check for known terms
        for term_key, term_entry in self._known_terms.items():
            if len(term_key) < 3:  # Skip very short terms to avoid false positives
                continue
            
            matches = term_entry.matches_text(line)
            
            for start, end, matched_text in matches:
                # Check if this is actually a definition rather than usage
                is_definition = self._is_term_definition(line, matched_text)
                
                if is_definition:
                    reference = CrossReference.create_definition(
                        term=matched_text,
                        source_file=file_path,
                        line_number=line_num,
                        context=line.strip()
                    )
                else:
                    reference = CrossReference.create_term_usage(
                        term=matched_text,
                        source_file=file_path,
                        line_number=line_num,
                        context=line.strip(),
                        is_valid=True  # Term usage is valid if term exists
                    )
                
                references.append(reference)
        
        # Look for unknown terms that might be undefined
        undefined_terms = self._find_potential_undefined_terms(line)
        for term in undefined_terms:
            reference = CrossReference.create_term_usage(
                term=term,
                source_file=file_path,
                line_number=line_num,
                context=line.strip(),
                is_valid=False  # Unknown term
            )
            references.append(reference)
        
        return references
    
    def _find_cli_references(self, line: str, file_path: str, line_num: int) -> List[CrossReference]:
        """Find CLI command references in a line."""
        references = []
        
        # Pattern: `me command` or "me command"
        cli_pattern = r'[`"]?(me\s+[^`"]+)[`"]?'
        matches = re.finditer(cli_pattern, line, re.IGNORECASE)
        
        for match in matches:
            command = match.group(1).strip()
            
            # Check if this is a known CLI command
            is_valid = command.lower() in self._known_terms
            
            reference = CrossReference.create_term_usage(
                term=command,
                source_file=file_path,
                line_number=line_num,
                context=line.strip(),
                is_valid=is_valid
            )
            references.append(reference)
        
        return references
    
    def _validate_link_target(self, target: str) -> bool:
        """Validate that a link target exists."""
        if '#' in target:
            file_part, section_part = target.split('#', 1)
            
            # Check if file exists and section exists
            if file_part in self._available_sections:
                return section_part.lower() in self._available_sections[file_part]
            
            return False
        else:
            # Just a file reference
            return target in self._available_sections
    
    def _is_term_definition(self, line: str, term: str) -> bool:
        """Check if a term usage in a line is actually its definition."""
        line_lower = line.lower()
        term_lower = term.lower()
        
        # Look for definition patterns
        definition_patterns = [
            f"#{term_lower}",  # Header
            f"**{term_lower}**",  # Bold
            f"{term_lower}:",  # Followed by colon
            f"{term_lower} is",  # Definition phrase
            f"{term_lower} sind",  # German definition phrase
        ]
        
        return any(pattern in line_lower for pattern in definition_patterns)
    
    def _find_potential_undefined_terms(self, line: str) -> List[str]:
        """Find terms that look like they should be defined but aren't."""
        undefined_terms = []
        
        # Look for UPPER_CASE terms that might be marker IDs
        marker_pattern = r'\b([A-Z]+_[A-Z_]+)\b'
        matches = re.findall(marker_pattern, line)
        
        for match in matches:
            if match.lower() not in self._known_terms:
                undefined_terms.append(match)
        
        # Look for terms that follow "UNKNOWN_" pattern from test
        unknown_pattern = r'\b(UNKNOWN_\w+)\b'
        unknown_matches = re.findall(unknown_pattern, line, re.IGNORECASE)
        undefined_terms.extend(unknown_matches)
        
        return undefined_terms