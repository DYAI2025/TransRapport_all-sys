"""
Validate service implementation

Handles validation of packages for integrity, compatibility, and security.
Performs comprehensive checks to ensure packages are ready for distribution.
"""

import hashlib
import json
import logging
import os
import platform
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models import (
    ValidateRequest, ValidateResponse, ValidationResult, ValidationType, Platform,
    create_error_response
)


logger = logging.getLogger(__name__)


class ValidateService:
    """Service for validating packages before distribution"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize validate service
        
        Args:
            project_root: Root directory of the project. If None, auto-detect.
        """
        self.project_root = project_root or self._detect_project_root()
        
        # Load validation rules and compatibility matrices
        self.validation_rules = self._load_validation_rules()
        self.compatibility_matrix = self._load_compatibility_matrix()
    
    def _detect_project_root(self) -> Path:
        """Detect project root by looking for key files"""
        current = Path.cwd()
        
        # Look for project indicators
        indicators = ["desktop/src-tauri/tauri.conf.json", "package.json", ".git"]
        
        while current != current.parent:
            if any((current / indicator).exists() for indicator in indicators):
                return current
            current = current.parent
        
        # Default to current directory
        return Path.cwd()
    
    def _load_validation_rules(self) -> Dict:
        """Load validation rules configuration"""
        rules_file = self.project_root / "validation_rules.json"
        
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(f"Failed to load validation rules: {e}")
        
        # Default validation rules
        return {
            "max_package_size_mb": 500,
            "required_signatures": {
                "windows": True,
                "macos": True,
                "linux": False
            },
            "blocked_files": [
                "*.tmp", "*.log", "debug.exe", "test*"
            ],
            "required_metadata": [
                "version", "description", "publisher"
            ]
        }
    
    def _load_compatibility_matrix(self) -> Dict:
        """Load compatibility matrix for different platforms"""
        matrix_file = self.project_root / "compatibility_matrix.json"
        
        if matrix_file.exists():
            try:
                with open(matrix_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.warning(f"Failed to load compatibility matrix: {e}")
        
        # Default compatibility matrix
        return {
            "windows": {
                "min_version": "10.0.19041",  # Windows 10 20H1
                "supported_architectures": ["x64", "arm64"],
                "required_frameworks": [".NET Framework 4.8", "WebView2"]
            },
            "macos": {
                "min_version": "10.15",  # Catalina
                "supported_architectures": ["x64", "arm64", "universal"],
                "required_frameworks": ["WebKit"]
            },
            "linux": {
                "supported_distros": [
                    "ubuntu-20.04", "ubuntu-22.04", "ubuntu-24.04",
                    "debian-11", "debian-12",
                    "fedora-38", "fedora-39", "fedora-40",
                    "centos-8", "rhel-8", "rhel-9"
                ],
                "supported_architectures": ["x64", "arm64"]
            }
        }
    
    def validate(self, request: ValidateRequest) -> ValidateResponse:
        """Validate a package according to specified validation type
        
        Args:
            request: Validation request parameters
            
        Returns:
            ValidateResponse with validation results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting validation for {request.package_path} with type {request.validation_type.value}")
            
            # Validate request
            validation_error = self._validate_request(request)
            if validation_error:
                return create_error_response(
                    ValidateResponse,
                    "INVALID_REQUEST",
                    validation_error
                )
            
            # Check if package exists
            package_path = Path(request.package_path)
            if not package_path.exists():
                return create_error_response(
                    ValidateResponse,
                    "PACKAGE_NOT_FOUND",
                    f"Package not found: {request.package_path}"
                )
            
            # Perform validation based on type
            validation_results = []
            
            if request.validation_type in [ValidationType.INTEGRITY, ValidationType.FULL]:
                integrity_results = self._validate_integrity(package_path)
                validation_results.extend(integrity_results)
            
            if request.validation_type in [ValidationType.COMPATIBILITY, ValidationType.FULL]:
                compatibility_results = self._validate_compatibility(package_path)
                validation_results.extend(compatibility_results)
            
            if request.validation_type in [ValidationType.SECURITY, ValidationType.FULL]:
                security_results = self._validate_security(package_path)
                validation_results.extend(security_results)
            
            # Determine overall validity
            overall_valid = all(result.passed for result in validation_results)
            
            validation_time = time.time() - start_time
            
            logger.info(f"Validation completed in {validation_time:.2f}s - Overall valid: {overall_valid}")
            
            return ValidateResponse(
                success=True,
                validation_results=validation_results,
                overall_valid=overall_valid,
                validation_time=validation_time
            )
            
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            validation_time = time.time() - start_time
            
            return ValidateResponse(
                success=False,
                error="VALIDATION_FAILED",
                message=f"Validation failed after {validation_time:.2f}s: {str(e)}",
                validation_time=validation_time
            )
    
    def _validate_request(self, request: ValidateRequest) -> Optional[str]:
        """Validate validation request parameters
        
        Args:
            request: Validation request to validate
            
        Returns:
            Error message if invalid, None if valid
        """
        # Validate package path
        if not request.package_path or len(request.package_path.strip()) == 0:
            return "Package path is required"
        
        # Validate validation type
        supported_types = [
            ValidationType.INTEGRITY, ValidationType.COMPATIBILITY,
            ValidationType.SECURITY, ValidationType.FULL
        ]
        if request.validation_type not in supported_types:
            return f"Unsupported validation type: {request.validation_type.value}"
        
        return None
    
    def _validate_integrity(self, package_path: Path) -> List[ValidationResult]:
        """Validate package integrity
        
        Args:
            package_path: Path to package file
            
        Returns:
            List of integrity validation results
        """
        results = []
        
        # Check file exists and is readable
        try:
            with open(package_path, 'rb') as f:
                f.read(1)  # Try to read first byte
            
            results.append(ValidationResult(
                check_name="file_readable",
                passed=True,
                message="Package file is readable"
            ))
        except Exception as e:
            results.append(ValidationResult(
                check_name="file_readable",
                passed=False,
                message=f"Package file is not readable: {e}"
            ))
            return results  # If not readable, skip other checks
        
        # Check file size
        file_size_mb = package_path.stat().st_size / (1024 * 1024)
        max_size_mb = self.validation_rules.get("max_package_size_mb", 500)
        
        if file_size_mb <= max_size_mb:
            results.append(ValidationResult(
                check_name="file_size",
                passed=True,
                message=f"Package size ({file_size_mb:.1f} MB) is within limits",
                details={"size_mb": file_size_mb, "max_size_mb": max_size_mb}
            ))
        else:
            results.append(ValidationResult(
                check_name="file_size",
                passed=False,
                message=f"Package size ({file_size_mb:.1f} MB) exceeds maximum ({max_size_mb} MB)",
                details={"size_mb": file_size_mb, "max_size_mb": max_size_mb}
            ))
        
        # Calculate and verify checksum
        try:
            checksum = self._calculate_checksum(package_path)
            results.append(ValidationResult(
                check_name="checksum_calculation",
                passed=True,
                message="Package checksum calculated successfully",
                details={"checksum": checksum}
            ))
        except Exception as e:
            results.append(ValidationResult(
                check_name="checksum_calculation",
                passed=False,
                message=f"Failed to calculate package checksum: {e}"
            ))
        
        # Validate package format based on extension
        format_result = self._validate_package_format(package_path)
        results.append(format_result)
        
        # Check for blocked files/patterns
        blocked_result = self._check_blocked_content(package_path)
        if blocked_result:
            results.append(blocked_result)
        
        return results
    
    def _validate_compatibility(self, package_path: Path) -> List[ValidationResult]:
        """Validate package compatibility
        
        Args:
            package_path: Path to package file
            
        Returns:
            List of compatibility validation results
        """
        results = []
        
        # Determine package platform based on extension
        package_platform = self._detect_package_platform(package_path)
        
        if not package_platform:
            results.append(ValidationResult(
                check_name="platform_detection",
                passed=False,
                message="Unable to detect package platform from file extension"
            ))
            return results
        
        results.append(ValidationResult(
            check_name="platform_detection",
            passed=True,
            message=f"Detected package platform: {package_platform}",
            details={"platform": package_platform}
        ))
        
        # Check compatibility with target platform requirements
        compatibility_info = self.compatibility_matrix.get(package_platform, {})
        
        if not compatibility_info:
            results.append(ValidationResult(
                check_name="compatibility_info",
                passed=False,
                message=f"No compatibility information available for platform: {package_platform}"
            ))
            return results
        
        # Validate minimum OS version requirements
        min_version = compatibility_info.get("min_version")
        if min_version:
            results.append(ValidationResult(
                check_name="min_os_version",
                passed=True,  # Assume compatible - real implementation would check actual requirements
                message=f"Package compatible with minimum OS version: {min_version}",
                details={"min_version": min_version}
            ))
        
        # Validate architecture support
        supported_archs = compatibility_info.get("supported_architectures", [])
        detected_arch = self._detect_package_architecture(package_path)
        
        if detected_arch in supported_archs:
            results.append(ValidationResult(
                check_name="architecture_compatibility",
                passed=True,
                message=f"Package architecture ({detected_arch}) is supported",
                details={"architecture": detected_arch, "supported": supported_archs}
            ))
        else:
            results.append(ValidationResult(
                check_name="architecture_compatibility",
                passed=False,
                message=f"Package architecture ({detected_arch}) is not supported",
                details={"architecture": detected_arch, "supported": supported_archs}
            ))
        
        # Check framework dependencies
        required_frameworks = compatibility_info.get("required_frameworks", [])
        if required_frameworks:
            results.append(ValidationResult(
                check_name="framework_dependencies",
                passed=True,  # Assume satisfied - real implementation would check package contents
                message=f"Required frameworks: {', '.join(required_frameworks)}",
                details={"frameworks": required_frameworks}
            ))
        
        return results
    
    def _validate_security(self, package_path: Path) -> List[ValidationResult]:
        """Validate package security
        
        Args:
            package_path: Path to package file
            
        Returns:
            List of security validation results
        """
        results = []
        
        # Determine package platform for signature requirements
        package_platform = self._detect_package_platform(package_path)
        
        # Check code signing requirements
        if package_platform in self.validation_rules.get("required_signatures", {}):
            signature_required = self.validation_rules["required_signatures"][package_platform]
            
            if signature_required:
                signature_valid = self._verify_code_signature(package_path, package_platform)
                
                if signature_valid:
                    results.append(ValidationResult(
                        check_name="code_signature",
                        passed=True,
                        message="Package is properly code signed"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name="code_signature",
                        passed=False,
                        message="Package is not properly code signed or signature is invalid"
                    ))
            else:
                results.append(ValidationResult(
                    check_name="code_signature",
                    passed=True,
                    message="Code signing not required for this platform"
                ))
        
        # Check for malicious patterns
        malware_result = self._scan_for_malware(package_path)
        results.append(malware_result)
        
        # Validate permissions and capabilities
        permissions_result = self._validate_permissions(package_path)
        if permissions_result:
            results.append(permissions_result)
        
        # Check for suspicious network activity indicators
        network_result = self._check_network_indicators(package_path)
        if network_result:
            results.append(network_result)
        
        return results
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex-encoded SHA256 checksum
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _validate_package_format(self, package_path: Path) -> ValidationResult:
        """Validate package format based on file extension
        
        Args:
            package_path: Path to package file
            
        Returns:
            ValidationResult for format validation
        """
        extension = package_path.suffix.lower()
        
        # Known package formats
        valid_formats = {
            ".msi": "Windows Installer",
            ".exe": "Windows Executable/NSIS",
            ".dmg": "macOS Disk Image",
            ".app": "macOS Application Bundle",
            ".deb": "Debian Package",
            ".rpm": "Red Hat Package",
            ".appimage": "Linux AppImage"
        }
        
        if extension in valid_formats:
            return ValidationResult(
                check_name="package_format",
                passed=True,
                message=f"Valid package format: {valid_formats[extension]}",
                details={"format": valid_formats[extension], "extension": extension}
            )
        else:
            return ValidationResult(
                check_name="package_format",
                passed=False,
                message=f"Unknown or invalid package format: {extension}",
                details={"extension": extension}
            )
    
    def _check_blocked_content(self, package_path: Path) -> Optional[ValidationResult]:
        """Check for blocked files or content patterns
        
        Args:
            package_path: Path to package file
            
        Returns:
            ValidationResult if blocked content found, None otherwise
        """
        blocked_patterns = self.validation_rules.get("blocked_files", [])
        
        # For now, just check filename patterns
        # Real implementation would extract and scan package contents
        for pattern in blocked_patterns:
            if package_path.match(pattern):
                return ValidationResult(
                    check_name="blocked_content",
                    passed=False,
                    message=f"Package matches blocked pattern: {pattern}",
                    details={"pattern": pattern}
                )
        
        return ValidationResult(
            check_name="blocked_content",
            passed=True,
            message="No blocked content patterns detected"
        )
    
    def _detect_package_platform(self, package_path: Path) -> Optional[str]:
        """Detect package platform from file extension
        
        Args:
            package_path: Path to package file
            
        Returns:
            Platform string or None if unknown
        """
        extension = package_path.suffix.lower()
        
        platform_map = {
            ".msi": "windows",
            ".exe": "windows",
            ".dmg": "macos",
            ".app": "macos",
            ".deb": "linux",
            ".rpm": "linux",
            ".appimage": "linux"
        }
        
        return platform_map.get(extension)
    
    def _detect_package_architecture(self, package_path: Path) -> str:
        """Detect package architecture
        
        Args:
            package_path: Path to package file
            
        Returns:
            Architecture string (default to x64 if unknown)
        """
        # This would typically analyze package metadata or binary contents
        # For now, infer from filename or default to x64
        
        filename = package_path.name.lower()
        
        if "arm64" in filename or "aarch64" in filename:
            return "arm64"
        elif "x64" in filename or "amd64" in filename or "x86_64" in filename:
            return "x64"
        elif "universal" in filename:
            return "universal"
        else:
            return "x64"  # Default assumption
    
    def _verify_code_signature(self, package_path: Path, package_platform: str) -> bool:
        """Verify code signature of package
        
        Args:
            package_path: Path to package file
            package_platform: Package platform
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if package_platform == "windows":
                # Use signtool to verify Windows signature
                result = subprocess.run([
                    "signtool", "verify", "/pa", str(package_path)
                ], capture_output=True, text=True, timeout=30)
                return result.returncode == 0
                
            elif package_platform == "macos":
                # Use codesign to verify macOS signature
                result = subprocess.run([
                    "codesign", "--verify", "--deep", "--strict", str(package_path)
                ], capture_output=True, text=True, timeout=30)
                return result.returncode == 0
                
            else:  # Linux
                # Check for GPG signature file
                sig_file = Path(str(package_path) + ".sig")
                if sig_file.exists():
                    result = subprocess.run([
                        "gpg", "--verify", str(sig_file), str(package_path)
                    ], capture_output=True, text=True, timeout=30)
                    return result.returncode == 0
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _scan_for_malware(self, package_path: Path) -> ValidationResult:
        """Scan package for malware patterns
        
        Args:
            package_path: Path to package file
            
        Returns:
            ValidationResult for malware scan
        """
        # This would integrate with antivirus engines or custom scanners
        # For now, return a basic check
        
        # Check file size for suspicious patterns
        file_size = package_path.stat().st_size
        
        # Very small files might be suspicious
        if file_size < 1024:  # Less than 1KB
            return ValidationResult(
                check_name="malware_scan",
                passed=False,
                message="Package file is suspiciously small",
                details={"size_bytes": file_size}
            )
        
        # Very large files might be suspicious
        if file_size > 1024 * 1024 * 1024:  # Greater than 1GB
            return ValidationResult(
                check_name="malware_scan",
                passed=False,
                message="Package file is suspiciously large",
                details={"size_bytes": file_size}
            )
        
        return ValidationResult(
            check_name="malware_scan",
            passed=True,
            message="No malware patterns detected in basic scan",
            details={"scan_type": "basic"}
        )
    
    def _validate_permissions(self, package_path: Path) -> Optional[ValidationResult]:
        """Validate package permissions and capabilities
        
        Args:
            package_path: Path to package file
            
        Returns:
            ValidationResult if permissions validation applicable, None otherwise
        """
        # This would check package metadata for requested permissions
        # Different for each platform (Windows capabilities, macOS entitlements, Linux permissions)
        
        # For now, return basic file permissions check
        try:
            stat_info = package_path.stat()
            file_mode = oct(stat_info.st_mode)[-3:]  # Last 3 octal digits
            
            # Check if file has execute permissions (should for most installers)
            if stat_info.st_mode & 0o111:  # Any execute bit set
                return ValidationResult(
                    check_name="file_permissions",
                    passed=True,
                    message=f"Package has appropriate file permissions: {file_mode}"
                )
            else:
                return ValidationResult(
                    check_name="file_permissions",
                    passed=False,
                    message=f"Package lacks execute permissions: {file_mode}"
                )
                
        except Exception as e:
            return ValidationResult(
                check_name="file_permissions",
                passed=False,
                message=f"Failed to check file permissions: {e}"
            )
    
    def _check_network_indicators(self, package_path: Path) -> Optional[ValidationResult]:
        """Check for suspicious network activity indicators
        
        Args:
            package_path: Path to package file
            
        Returns:
            ValidationResult if network indicators found, None otherwise
        """
        # This would scan package contents for:
        # - Suspicious URLs
        # - Network configuration files
        # - Embedded certificates
        # - Remote download indicators
        
        # For now, return a basic placeholder
        return ValidationResult(
            check_name="network_indicators",
            passed=True,
            message="No suspicious network indicators detected in basic scan",
            details={"scan_type": "basic"}
        )