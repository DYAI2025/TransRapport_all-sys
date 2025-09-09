"""ValidationEngine service for orchestrating documentation validation."""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from ..models.validation_result import ValidationResult, Severity
from ..models.documentation_file import DocumentationFile, ValidationStatus
from ..services.doc_parser import DocumentationParser
from ..services.terminology_extractor import TerminologyExtractor
from ..services.crossref_validator import CrossReferenceValidator


class ValidationEngine:
    """Service for orchestrating documentation validation."""
    
    def __init__(self):
        self.doc_parser = DocumentationParser()
        self.terminology_extractor = TerminologyExtractor()
        self.crossref_validator = CrossReferenceValidator()
    
    def validate_directory(self, directory_path: Path, strict: bool = False) -> Dict[str, any]:
        """Validate all documentation in a directory."""
        if not directory_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}",
                "file_count": 0,
                "issues": []
            }
        
        # Parse all documentation files
        doc_files = self.doc_parser.parse_directory(directory_path)
        
        if not doc_files:
            return {
                "success": True,
                "file_count": 0,
                "issues": [],
                "summary": {"errors": 0, "warnings": 0, "info": 0}
            }
        
        # Validate each file
        all_issues = []
        
        for doc_file in doc_files:
            file_issues = self.validate_file(doc_file, strict=strict)
            all_issues.extend(file_issues)
        
        # Validate cross-references across all files
        cross_ref_issues = self._validate_cross_references(directory_path, strict=strict)
        all_issues.extend(cross_ref_issues)
        
        # Calculate summary
        summary = self._calculate_summary(all_issues)
        success = summary["errors"] == 0 or (not strict and summary["errors"] == 0)
        
        return {
            "success": success,
            "file_count": len(doc_files),
            "issues": [issue.to_dict() for issue in all_issues],
            "summary": summary
        }
    
    def validate_file(self, doc_file: DocumentationFile, strict: bool = False) -> List[ValidationResult]:
        """Validate a single documentation file."""
        issues = []
        
        try:
            # Basic file validation
            if not doc_file.path.exists():
                issues.append(ValidationResult.create_error(
                    file_path=str(doc_file.path),
                    rule_name="file_exists",
                    message="File does not exist"
                ))
                return issues
            
            # Read file content
            content = doc_file.path.read_text(encoding='utf-8', errors='ignore')
            
            # Validate markdown structure
            structure_issues = self._validate_markdown_structure(doc_file, content, strict)
            issues.extend(structure_issues)
            
            # Validate content completeness
            content_issues = self._validate_content_completeness(doc_file, content, strict)
            issues.extend(content_issues)
            
            # Update file validation status
            if any(issue.severity == Severity.ERROR for issue in issues):
                doc_file.update_validation_status(ValidationStatus.INVALID)
            else:
                doc_file.update_validation_status(ValidationStatus.VALID)
        
        except Exception as e:
            issues.append(ValidationResult.create_error(
                file_path=str(doc_file.path),
                rule_name="file_parsing",
                message=f"Failed to parse file: {str(e)}"
            ))
            doc_file.update_validation_status(ValidationStatus.INVALID)
        
        return issues
    
    def _validate_markdown_structure(self, doc_file: DocumentationFile, content: str, strict: bool) -> List[ValidationResult]:
        """Validate basic markdown structure."""
        issues = []
        lines = content.split('\n')
        
        # Check for main title
        has_main_title = False
        for i, line in enumerate(lines[:10], 1):  # Check first 10 lines
            if line.strip().startswith('#') and not line.strip().startswith('##'):
                has_main_title = True
                break
        
        if not has_main_title:
            severity = Severity.ERROR if strict else Severity.WARNING
            issues.append(ValidationResult(
                file_path=str(doc_file.path),
                rule_name="markdown_structure",
                severity=severity,
                line_number=1,
                message="Document should start with a main title (# Title)",
                suggestion="Add a main title at the beginning of the document",
                validated_at=datetime.now()
            ))
        
        # Check for broken markdown links syntax
        for i, line in enumerate(lines, 1):
            # Find potential broken links
            if '[' in line and ']' in line:
                # Check for malformed links like [text]( or [text](unclosed
                if '](' in line:
                    open_parens = line.count('](')
                    close_parens = line.count(')')
                    if open_parens > close_parens:
                        issues.append(ValidationResult.create_warning(
                            file_path=str(doc_file.path),
                            rule_name="markdown_syntax",
                            message="Potentially broken markdown link syntax",
                            line_number=i,
                            suggestion="Check that all markdown links are properly closed"
                        ))
        
        return issues
    
    def _validate_content_completeness(self, doc_file: DocumentationFile, content: str, strict: bool) -> List[ValidationResult]:
        """Validate content completeness."""
        issues = []
        
        # Check minimum content length
        if len(content.strip()) < 100:
            severity = Severity.WARNING if not strict else Severity.ERROR
            issues.append(ValidationResult(
                file_path=str(doc_file.path),
                rule_name="content_completeness",
                severity=severity,
                line_number=None,
                message="Document appears to be very short or empty",
                suggestion="Add meaningful content to the document",
                validated_at=datetime.now()
            ))
        
        # File-specific validations
        if doc_file.name == "terminologie":
            terminology_issues = self._validate_terminologie_content(doc_file, content, strict)
            issues.extend(terminology_issues)
        elif doc_file.name == "marker":
            marker_issues = self._validate_marker_content(doc_file, content, strict)
            issues.extend(marker_issues)
        
        return issues
    
    def _validate_terminologie_content(self, doc_file: DocumentationFile, content: str, strict: bool) -> List[ValidationResult]:
        """Validate terminologie.md specific content."""
        issues = []
        
        # Check for key marker terms
        key_terms = ['ATO', 'SEM', 'CLU', 'MEMA']
        missing_terms = []
        
        for term in key_terms:
            if term not in content:
                missing_terms.append(term)
        
        if missing_terms:
            severity = Severity.ERROR if strict else Severity.WARNING
            issues.append(ValidationResult(
                file_path=str(doc_file.path),
                rule_name="terminology_completeness",
                severity=severity,
                line_number=None,
                message=f"Missing key marker terms: {', '.join(missing_terms)}",
                suggestion="Add definitions for all marker levels (ATO, SEM, CLU, MEMA)",
                validated_at=datetime.now()
            ))
        
        return issues
    
    def _validate_marker_content(self, doc_file: DocumentationFile, content: str, strict: bool) -> List[ValidationResult]:
        """Validate marker.md specific content."""
        issues = []
        
        # Check for LD-3.4 compliance mentions
        if "LD-3.4" not in content and "ld-3.4" not in content.lower():
            severity = Severity.WARNING
            issues.append(ValidationResult(
                file_path=str(doc_file.path),
                rule_name="ld34_compliance",
                severity=severity,
                line_number=None,
                message="No mention of LD-3.4 specification found",
                suggestion="Reference LD-3.4 specification for marker compliance",
                validated_at=datetime.now()
            ))
        
        return issues
    
    def _validate_cross_references(self, directory_path: Path, strict: bool) -> List[ValidationResult]:
        """Validate cross-references across all files."""
        issues = []
        
        try:
            cross_refs = self.crossref_validator.validate_directory(directory_path)
            
            for cross_ref in cross_refs:
                if not cross_ref.is_valid:
                    severity = Severity.ERROR if strict else Severity.WARNING
                    
                    if cross_ref.reference_type.value == "link":
                        message = f"Broken cross-reference: {cross_ref.term}"
                        suggestion = "Check that the target file and section exist"
                    else:
                        message = f"Undefined term: {cross_ref.term}"
                        suggestion = "Define this term in terminologie.md or verify spelling"
                    
                    issues.append(ValidationResult(
                        file_path=cross_ref.source_file,
                        rule_name="cross_reference",
                        severity=severity,
                        line_number=cross_ref.line_number,
                        message=message,
                        suggestion=suggestion,
                        validated_at=datetime.now()
                    ))
        
        except Exception:
            # Cross-reference validation failed, but don't fail entire validation
            pass
        
        return issues
    
    def _calculate_summary(self, issues: List[ValidationResult]) -> Dict[str, int]:
        """Calculate summary statistics for validation results."""
        summary = {"errors": 0, "warnings": 0, "info": 0}
        
        for issue in issues:
            if issue.severity == Severity.ERROR:
                summary["errors"] += 1
            elif issue.severity == Severity.WARNING:
                summary["warnings"] += 1
            elif issue.severity == Severity.INFO:
                summary["info"] += 1
        
        return summary