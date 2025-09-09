"""
Data models for the packaging system

These models define the request/response structures for all packaging operations.
They ensure type safety and validation across the entire packaging pipeline.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from pathlib import Path


class Platform(Enum):
    """Supported target platforms"""
    WINDOWS_11 = "windows-11"
    MACOS = "macos"
    LINUX_DEB = "linux-deb"
    LINUX_RPM = "linux-rpm"
    LINUX_APPIMAGE = "linux-appimage"


class Architecture(Enum):
    """Supported CPU architectures"""
    X64 = "x64"
    ARM64 = "arm64"
    UNIVERSAL = "universal"  # macOS universal binary


class Profile(Enum):
    """Build profiles"""
    DEBUG = "debug"
    RELEASE = "release"


class BundleType(Enum):
    """Package bundle types"""
    MSI = "msi"
    EXE = "exe"  # NSIS installer
    DMG = "dmg"
    APP = "app"  # macOS app bundle
    DEB = "deb"
    RPM = "rpm"
    APPIMAGE = "appimage"


class ValidationType(Enum):
    """Package validation types"""
    INTEGRITY = "integrity"
    COMPATIBILITY = "compatibility"
    SECURITY = "security"
    FULL = "full"


class CertificateSource(Enum):
    """Code signing certificate sources"""
    AZURE_KEY_VAULT = "azure_key_vault"
    APPLE_DEVELOPER = "apple_developer"
    LOCAL_CERTIFICATE = "local_certificate"


class OutputFormat(Enum):
    """Output format for CLI responses"""
    JSON = "json"
    HUMAN = "human"


# Request Models

@dataclass
class BuildRequest:
    """Request model for POST /build endpoint"""
    platform: Platform
    version: str
    profile: Profile
    architecture: Optional[Architecture] = None
    
    def __post_init__(self):
        """Validate request after initialization"""
        # Convert string enums to enum instances if needed
        if isinstance(self.platform, str):
            self.platform = Platform(self.platform)
        if isinstance(self.profile, str):
            self.profile = Profile(self.profile)
        if isinstance(self.architecture, str):
            self.architecture = Architecture(self.architecture)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "platform": self.platform.value,
            "version": self.version,
            "profile": self.profile.value,
            "architecture": self.architecture.value if self.architecture else None
        }


@dataclass
class PackageRequest:
    """Request model for POST /package endpoint"""
    build_id: str
    bundle_type: BundleType
    signing_required: bool = False
    
    def __post_init__(self):
        """Validate request after initialization"""
        if isinstance(self.bundle_type, str):
            self.bundle_type = BundleType(self.bundle_type)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "build_id": self.build_id,
            "bundle_type": self.bundle_type.value,
            "signing_required": self.signing_required
        }


@dataclass
class SignRequest:
    """Request model for POST /sign endpoint"""
    package_path: str
    platform: Platform
    certificate_source: CertificateSource
    
    def __post_init__(self):
        """Validate request after initialization"""
        if isinstance(self.platform, str):
            self.platform = Platform(self.platform)
        if isinstance(self.certificate_source, str):
            self.certificate_source = CertificateSource(self.certificate_source)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "package_path": self.package_path,
            "platform": self.platform.value,
            "certificate_source": self.certificate_source.value
        }


@dataclass
class ValidateRequest:
    """Request model for POST /validate endpoint"""
    package_path: str
    validation_type: ValidationType
    
    def __post_init__(self):
        """Validate request after initialization"""
        if isinstance(self.validation_type, str):
            self.validation_type = ValidationType(self.validation_type)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "package_path": self.package_path,
            "validation_type": self.validation_type.value
        }


# Response Models

@dataclass
class BuildArtifact:
    """Build artifact information"""
    path: str
    size: int
    checksum: str
    architecture: Architecture
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "path": self.path,
            "size": self.size,
            "checksum": self.checksum,
            "architecture": self.architecture.value
        }


@dataclass
class BuildResponse:
    """Response model for POST /build endpoint"""
    success: bool
    build_id: Optional[str] = None
    artifacts: Optional[List[BuildArtifact]] = None
    build_time: Optional[float] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {"success": self.success}
        
        if self.build_id:
            result["build_id"] = self.build_id
        if self.artifacts:
            result["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        if self.build_time is not None:
            result["build_time"] = self.build_time
        if self.error:
            result["error"] = self.error
        if self.message:
            result["message"] = self.message
            
        return result


@dataclass
class PackageInfo:
    """Package information"""
    path: str
    size: int
    checksum: str
    bundle_type: BundleType
    signed: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "path": self.path,
            "size": self.size,
            "checksum": self.checksum,
            "bundle_type": self.bundle_type.value,
            "signed": self.signed
        }


@dataclass
class PackageResponse:
    """Response model for POST /package endpoint"""
    success: bool
    package: Optional[PackageInfo] = None
    package_time: Optional[float] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {"success": self.success}
        
        if self.package:
            result["package"] = self.package.to_dict()
        if self.package_time is not None:
            result["package_time"] = self.package_time
        if self.error:
            result["error"] = self.error
        if self.message:
            result["message"] = self.message
            
        return result


@dataclass
class SignatureInfo:
    """Code signature information"""
    algorithm: str
    timestamp: datetime
    certificate_subject: str
    valid: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "algorithm": self.algorithm,
            "timestamp": self.timestamp.isoformat(),
            "certificate_subject": self.certificate_subject,
            "valid": self.valid
        }


@dataclass
class SignResponse:
    """Response model for POST /sign endpoint"""
    success: bool
    signature: Optional[SignatureInfo] = None
    signed_package_path: Optional[str] = None
    signing_time: Optional[float] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {"success": self.success}
        
        if self.signature:
            result["signature"] = self.signature.to_dict()
        if self.signed_package_path:
            result["signed_package_path"] = self.signed_package_path
        if self.signing_time is not None:
            result["signing_time"] = self.signing_time
        if self.error:
            result["error"] = self.error
        if self.message:
            result["message"] = self.message
            
        return result


@dataclass
class ValidationResult:
    """Validation result for a specific check"""
    check_name: str
    passed: bool
    message: str
    details: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {
            "check_name": self.check_name,
            "passed": self.passed,
            "message": self.message
        }
        
        if self.details:
            result["details"] = self.details
            
        return result


@dataclass
class ValidateResponse:
    """Response model for POST /validate endpoint"""
    success: bool
    validation_results: Optional[List[ValidationResult]] = None
    overall_valid: Optional[bool] = None
    validation_time: Optional[float] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {"success": self.success}
        
        if self.validation_results:
            result["validation_results"] = [vr.to_dict() for vr in self.validation_results]
        if self.overall_valid is not None:
            result["overall_valid"] = self.overall_valid
        if self.validation_time is not None:
            result["validation_time"] = self.validation_time
        if self.error:
            result["error"] = self.error
        if self.message:
            result["message"] = self.message
            
        return result


# Utility Functions

def create_error_response(response_class, error_code: str, message: str):
    """Create standardized error response"""
    return response_class(
        success=False,
        error=error_code,
        message=message
    )


def validate_version_format(version: str) -> bool:
    """Validate semantic version format (x.y.z)"""
    import re
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-]+))?(?:\+([a-zA-Z0-9\-]+))?$'
    return bool(re.match(pattern, version))


def get_platform_bundle_types(platform: Platform) -> List[BundleType]:
    """Get supported bundle types for a platform"""
    platform_bundles = {
        Platform.WINDOWS_11: [BundleType.MSI, BundleType.EXE],
        Platform.MACOS: [BundleType.DMG, BundleType.APP],
        Platform.LINUX_DEB: [BundleType.DEB],
        Platform.LINUX_RPM: [BundleType.RPM],
        Platform.LINUX_APPIMAGE: [BundleType.APPIMAGE]
    }
    
    return platform_bundles.get(platform, [])


def get_platform_architectures(platform: Platform) -> List[Architecture]:
    """Get supported architectures for a platform"""
    platform_architectures = {
        Platform.WINDOWS_11: [Architecture.X64, Architecture.ARM64],
        Platform.MACOS: [Architecture.X64, Architecture.ARM64, Architecture.UNIVERSAL],
        Platform.LINUX_DEB: [Architecture.X64, Architecture.ARM64],
        Platform.LINUX_RPM: [Architecture.X64, Architecture.ARM64],
        Platform.LINUX_APPIMAGE: [Architecture.X64, Architecture.ARM64]
    }
    
    return platform_architectures.get(platform, [Architecture.X64])


def get_certificate_source_for_platform(platform: Platform) -> CertificateSource:
    """Get default certificate source for a platform"""
    platform_certs = {
        Platform.WINDOWS_11: CertificateSource.AZURE_KEY_VAULT,
        Platform.MACOS: CertificateSource.APPLE_DEVELOPER,
        Platform.LINUX_DEB: CertificateSource.LOCAL_CERTIFICATE,
        Platform.LINUX_RPM: CertificateSource.LOCAL_CERTIFICATE,
        Platform.LINUX_APPIMAGE: CertificateSource.LOCAL_CERTIFICATE
    }
    
    return platform_certs.get(platform, CertificateSource.LOCAL_CERTIFICATE)