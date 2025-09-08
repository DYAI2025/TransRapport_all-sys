"""DocumentationParser service for parsing documentation files and extracting metadata."""
from pathlib import Path
from typing import Optional
import re

from ..models.documentation_file import DocumentationFile, ValidationStatus


class DocumentationParser:
    """Service for parsing documentation files and extracting metadata."""
    
    def parse_file(self, file_path: Path) -> DocumentationFile:
        """Parse a documentation file and extract metadata."""
        if not file_path.exists():
            raise FileNotFoundError(f"Documentation file not found: {file_path}")
        
        try:
            # Use DocumentationFile.from_path to create base object
            doc_file = DocumentationFile.from_path(file_path)
            
            # Read content for additional parsing
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Extract dependencies (markdown links to other files)
            doc_file.dependencies = self._extract_dependencies(content)
            
            return doc_file
            
        except Exception as e:
            # Create a basic file object even if parsing fails
            doc_file = DocumentationFile(
                path=file_path,
                name=file_path.stem.lower(),
                version="unknown",
                size_bytes=file_path.stat().st_size if file_path.exists() else 0,
                last_validated=None,
                validation_status=ValidationStatus.INVALID,
                dependencies=[]
            )
            return doc_file
    
    def _extract_dependencies(self, content: str) -> list[str]:
        """Extract file dependencies from markdown links."""
        dependencies = []
        
        # Pattern to match markdown links to other files
        # [text](filename.md) or [text](path/filename.md)
        link_pattern = r'\[([^\]]+)\]\(([^)]+\.md(?:#[^)]*)?)\)'
        
        matches = re.findall(link_pattern, content, re.IGNORECASE)
        
        for _, link_path in matches:
            # Clean up the link path (remove anchors)
            clean_path = link_path.split('#')[0]
            if clean_path not in dependencies:
                dependencies.append(clean_path)
        
        return dependencies
    
    def parse_directory(self, directory_path: Path) -> list[DocumentationFile]:
        """Parse all markdown files in a directory."""
        doc_files = []
        
        if not directory_path.exists() or not directory_path.is_dir():
            return doc_files
        
        # Find all markdown files
        for md_file in directory_path.glob('**/*.md'):
            try:
                doc_file = self.parse_file(md_file)
                doc_files.append(doc_file)
            except Exception:
                # Skip files that can't be parsed, but continue with others
                continue
        
        return doc_files
    
    def identify_transrapport_files(self, doc_files: list[DocumentationFile]) -> dict[str, Optional[DocumentationFile]]:
        """Identify the four core TransRapport documentation files."""
        result = {
            'transrapport': None,
            'architecture': None,
            'terminologie': None,
            'marker': None
        }
        
        for doc_file in doc_files:
            name_lower = doc_file.name.lower()
            path_lower = str(doc_file.path).lower()
            
            if 'transrapport' in name_lower or 'transrapport' in path_lower:
                result['transrapport'] = doc_file
            elif 'architecture' in name_lower or 'architecture' in path_lower:
                result['architecture'] = doc_file
            elif 'terminologie' in name_lower or 'terminologie' in path_lower:
                result['terminologie'] = doc_file
            elif 'marker' in name_lower or 'marker' in path_lower:
                result['marker'] = doc_file
        
        return result