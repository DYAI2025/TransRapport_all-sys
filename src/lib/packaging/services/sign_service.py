"""
Sign service implementation

Handles code signing for packages across different platforms.
Manages certificate loading, signing operations, and verification.
"""

import json
import logging
import os
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..models import (
    SignRequest, SignResponse, SignatureInfo, Platform, CertificateSource,
    create_error_response
)


logger = logging.getLogger(__name__)


class SignService:
    """Service for code signing packages across platforms"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize sign service
        
        Args:
            project_root: Root directory of the project. If None, auto-detect.
        """
        self.project_root = project_root or self._detect_project_root()
        self.certs_dir = self.project_root / "certs"
        
        # Load certificate configurations
        self.cert_configs = self._load_certificate_configs()
    
    def _detect_project_root(self) -> Path:
        """Detect project root by looking for key files"""
        current = Path.cwd()
        
        # Look for project indicators
        indicators = ["certs", "desktop/src-tauri/tauri.conf.json", ".git"]
        
        while current != current.parent:
            if any((current / indicator).exists() for indicator in indicators):
                return current
            current = current.parent
        
        # Default to current directory
        return Path.cwd()
    
    def _load_certificate_configs(self) -> Dict:
        """Load certificate configurations from certs directory"""
        configs = {}
        
        if not self.certs_dir.exists():
            logger.warning(f"Certificates directory not found: {self.certs_dir}")
            return configs
        
        # Load platform-specific certificate configs
        for platform_dir in self.certs_dir.iterdir():
            if platform_dir.is_dir():
                config_file = platform_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            configs[platform_dir.name] = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        logger.warning(f"Failed to load certificate config for {platform_dir.name}: {e}")
        
        return configs
    
    def sign(self, request: SignRequest) -> SignResponse:
        """Sign a package with appropriate certificate

        Args:
            request: Sign request parameters

        Returns:
            SignResponse with signing results
        """
        logger.info(
            "Signing requested for %s on %s – service not yet implemented",
            request.package_path,
            request.platform.value,
        )

        return create_error_response(
            SignResponse,
            "NOT_IMPLEMENTED",
            "Sign service not yet implemented for offline packaging pipeline.",
        )
    
    def _validate_sign_request(self, request: SignRequest) -> Optional[str]:
        """Validate sign request parameters
        
        Args:
            request: Sign request to validate
            
        Returns:
            Error message if invalid, None if valid
        """
        # Validate package path
        if not request.package_path or len(request.package_path.strip()) == 0:
            return "Package path is required"
        
        # Validate platform support
        supported_platforms = [Platform.WINDOWS_11, Platform.MACOS, Platform.LINUX_DEB, 
                             Platform.LINUX_RPM, Platform.LINUX_APPIMAGE]
        if request.platform not in supported_platforms:
            return f"Unsupported platform: {request.platform.value}"
        
        # Validate certificate source for platform
        valid_sources = self._get_valid_certificate_sources(request.platform)
        if request.certificate_source not in valid_sources:
            return f"Invalid certificate source {request.certificate_source.value} for platform {request.platform.value}"
        
        return None
    
    def _get_valid_certificate_sources(self, platform: Platform) -> List[CertificateSource]:
        """Get valid certificate sources for a platform
        
        Args:
            platform: Target platform
            
        Returns:
            List of valid certificate sources
        """
        platform_sources = {
            Platform.WINDOWS_11: [CertificateSource.AZURE_KEY_VAULT, CertificateSource.LOCAL_CERTIFICATE],
            Platform.MACOS: [CertificateSource.APPLE_DEVELOPER, CertificateSource.LOCAL_CERTIFICATE],
            Platform.LINUX_DEB: [CertificateSource.LOCAL_CERTIFICATE],
            Platform.LINUX_RPM: [CertificateSource.LOCAL_CERTIFICATE],
            Platform.LINUX_APPIMAGE: [CertificateSource.LOCAL_CERTIFICATE]
        }
        
        return platform_sources.get(platform, [CertificateSource.LOCAL_CERTIFICATE])
    
    def _get_certificate_config(self, platform: Platform, cert_source: CertificateSource) -> Optional[Dict]:
        """Get certificate configuration for platform and source
        
        Args:
            platform: Target platform
            cert_source: Certificate source
            
        Returns:
            Certificate configuration or None if not found
        """
        platform_name = platform.value.replace('-', '_')
        
        if platform_name not in self.cert_configs:
            return None
        
        platform_config = self.cert_configs[platform_name]
        source_name = cert_source.value
        
        return platform_config.get(source_name)
    
    def _perform_signing(self, request: SignRequest, cert_config: Dict, package_path: Path) -> SignResponse:
        """Perform signing operation based on platform
        
        Args:
            request: Sign request
            cert_config: Certificate configuration
            package_path: Path to package file
            
        Returns:
            SignResponse with signing results
        """
        if request.platform == Platform.WINDOWS_11:
            return self._sign_windows_package(request, cert_config, package_path)
        elif request.platform == Platform.MACOS:
            return self._sign_macos_package(request, cert_config, package_path)
        else:  # Linux platforms
            return self._sign_linux_package(request, cert_config, package_path)
    
    def _sign_windows_package(self, request: SignRequest, cert_config: Dict, package_path: Path) -> SignResponse:
        """Sign Windows package (MSI/EXE)
        
        Args:
            request: Sign request
            cert_config: Certificate configuration
            package_path: Path to package file
            
        Returns:
            SignResponse with signing results
        """
        if request.certificate_source == CertificateSource.AZURE_KEY_VAULT:
            return self._sign_windows_azure_key_vault(cert_config, package_path)
        else:  # LOCAL_CERTIFICATE
            return self._sign_windows_local_certificate(cert_config, package_path)
    
    def _sign_windows_azure_key_vault(self, cert_config: Dict, package_path: Path) -> SignResponse:
        """Sign Windows package using Azure Key Vault
        
        Args:
            cert_config: Certificate configuration
            package_path: Path to package file
            
        Returns:
            SignResponse with signing results
        """
        try:
            # Azure Key Vault signing requires:
            # - Azure CLI authentication
            # - Key Vault access permissions
            # - Certificate stored in Key Vault
            
            key_vault_url = cert_config.get("key_vault_url")
            certificate_name = cert_config.get("certificate_name")
            
            if not key_vault_url or not certificate_name:
                return create_error_response(
                    SignResponse,
                    "INVALID_AZURE_CONFIG",
                    "Azure Key Vault URL and certificate name are required"
                )
            
            # Use Azure SignTool or similar tool for Key Vault signing
            # This is a simplified implementation - real implementation would use
            # Azure SDK or specialized signing tools
            
            cmd = [
                "signtool", "sign",
                "/fd", "sha256",
                "/tr", "http://timestamp.sectigo.com",
                "/td", "sha256",
                "/kv", key_vault_url,
                "/kc", certificate_name,
                str(package_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Verify signature
                signature_info = self._verify_windows_signature(package_path)
                
                return SignResponse(
                    success=True,
                    signature=signature_info,
                    signed_package_path=str(package_path)
                )
            else:
                return create_error_response(
                    SignResponse,
                    "AZURE_SIGNING_FAILED",
                    f"Azure Key Vault signing failed: {result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            return create_error_response(
                SignResponse,
                "SIGNING_TIMEOUT",
                "Signing operation timed out"
            )
        except FileNotFoundError:
            return create_error_response(
                SignResponse,
                "SIGNTOOL_NOT_FOUND",
                "signtool.exe not found. Install Windows SDK."
            )
    
    def _sign_windows_local_certificate(self, cert_config: Dict, package_path: Path) -> SignResponse:
        """Sign Windows package using local certificate
        
        Args:
            cert_config: Certificate configuration
            package_path: Path to package file
            
        Returns:
            SignResponse with signing results
        """
        try:
            cert_path = cert_config.get("certificate_path")
            cert_password = cert_config.get("certificate_password")
            
            if not cert_path:
                return create_error_response(
                    SignResponse,
                    "INVALID_LOCAL_CERT_CONFIG",
                    "Certificate path is required for local certificate signing"
                )
            
            cert_file = Path(cert_path)
            if not cert_file.exists():
                return create_error_response(
                    SignResponse,
                    "CERTIFICATE_NOT_FOUND",
                    f"Certificate file not found: {cert_path}"
                )
            
            cmd = [
                "signtool", "sign",
                "/fd", "sha256",
                "/tr", "http://timestamp.sectigo.com",
                "/td", "sha256",
                "/f", str(cert_file)
            ]
            
            if cert_password:
                cmd.extend(["/p", cert_password])
            
            cmd.append(str(package_path))
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                signature_info = self._verify_windows_signature(package_path)
                
                return SignResponse(
                    success=True,
                    signature=signature_info,
                    signed_package_path=str(package_path)
                )
            else:
                return create_error_response(
                    SignResponse,
                    "LOCAL_SIGNING_FAILED",
                    f"Local certificate signing failed: {result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            return create_error_response(
                SignResponse,
                "SIGNING_TIMEOUT",
                "Signing operation timed out"
            )
        except FileNotFoundError:
            return create_error_response(
                SignResponse,
                "SIGNTOOL_NOT_FOUND",
                "signtool.exe not found. Install Windows SDK."
            )
    
    def _sign_macos_package(self, request: SignRequest, cert_config: Dict, package_path: Path) -> SignResponse:
        """Sign macOS package (DMG/APP)
        
        Args:
            request: Sign request
            cert_config: Certificate configuration
            package_path: Path to package file
            
        Returns:
            SignResponse with signing results
        """
        try:
            if request.certificate_source == CertificateSource.APPLE_DEVELOPER:
                developer_id = cert_config.get("developer_id")
                team_id = cert_config.get("team_id")
                
                if not developer_id:
                    return create_error_response(
                        SignResponse,
                        "INVALID_APPLE_CONFIG",
                        "Apple Developer ID is required"
                    )
                
                # Sign with codesign
                cmd = [
                    "codesign",
                    "--sign", developer_id,
                    "--deep",
                    "--force",
                    "--options", "runtime",
                    "--timestamp",
                    str(package_path)
                ]
                
            else:  # LOCAL_CERTIFICATE
                cert_identity = cert_config.get("certificate_identity")
                
                if not cert_identity:
                    return create_error_response(
                        SignResponse,
                        "INVALID_LOCAL_CERT_CONFIG",
                        "Certificate identity is required for local certificate signing"
                    )
                
                cmd = [
                    "codesign",
                    "--sign", cert_identity,
                    "--deep",
                    "--force",
                    str(package_path)
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                signature_info = self._verify_macos_signature(package_path)
                
                return SignResponse(
                    success=True,
                    signature=signature_info,
                    signed_package_path=str(package_path)
                )
            else:
                return create_error_response(
                    SignResponse,
                    "MACOS_SIGNING_FAILED",
                    f"macOS signing failed: {result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            return create_error_response(
                SignResponse,
                "SIGNING_TIMEOUT",
                "Signing operation timed out"
            )
        except FileNotFoundError:
            return create_error_response(
                SignResponse,
                "CODESIGN_NOT_FOUND",
                "codesign not found. Ensure Xcode command line tools are installed."
            )
    
    def _sign_linux_package(self, request: SignRequest, cert_config: Dict, package_path: Path) -> SignResponse:
        """Sign Linux package (DEB/RPM/AppImage)
        
        Args:
            request: Sign request
            cert_config: Certificate configuration
            package_path: Path to package file
            
        Returns:
            SignResponse with signing results
        """
        try:
            gpg_key_id = cert_config.get("gpg_key_id")
            gpg_passphrase = cert_config.get("gpg_passphrase")
            
            if not gpg_key_id:
                return create_error_response(
                    SignResponse,
                    "INVALID_GPG_CONFIG",
                    "GPG key ID is required for Linux package signing"
                )
            
            # Create detached signature
            signature_path = Path(str(package_path) + ".sig")
            
            cmd = ["gpg", "--armor", "--detach-sign"]
            
            if gpg_passphrase:
                cmd.extend(["--batch", "--yes", "--passphrase", gpg_passphrase])
            
            cmd.extend([
                "--default-key", gpg_key_id,
                "--output", str(signature_path),
                str(package_path)
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                signature_info = self._verify_linux_signature(package_path, signature_path)
                
                return SignResponse(
                    success=True,
                    signature=signature_info,
                    signed_package_path=str(signature_path)  # Return signature file path
                )
            else:
                return create_error_response(
                    SignResponse,
                    "LINUX_SIGNING_FAILED",
                    f"GPG signing failed: {result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            return create_error_response(
                SignResponse,
                "SIGNING_TIMEOUT",
                "Signing operation timed out"
            )
        except FileNotFoundError:
            return create_error_response(
                SignResponse,
                "GPG_NOT_FOUND",
                "gpg not found. Install GnuPG."
            )
    
    def _verify_windows_signature(self, package_path: Path) -> SignatureInfo:
        """Verify Windows package signature
        
        Args:
            package_path: Path to signed package
            
        Returns:
            SignatureInfo with verification results
        """
        try:
            # Use signtool to verify signature
            result = subprocess.run([
                "signtool", "verify", "/pa", str(package_path)
            ], capture_output=True, text=True)
            
            return SignatureInfo(
                algorithm="SHA256",
                timestamp=datetime.now(),
                certificate_subject="TransRapport Code Signing Certificate",
                valid=(result.returncode == 0)
            )
            
        except FileNotFoundError:
            # Fallback if signtool not available
            return SignatureInfo(
                algorithm="SHA256",
                timestamp=datetime.now(),
                certificate_subject="Unknown",
                valid=False
            )
    
    def _verify_macos_signature(self, package_path: Path) -> SignatureInfo:
        """Verify macOS package signature
        
        Args:
            package_path: Path to signed package
            
        Returns:
            SignatureInfo with verification results
        """
        try:
            # Use codesign to verify signature
            result = subprocess.run([
                "codesign", "--verify", "--deep", "--strict", str(package_path)
            ], capture_output=True, text=True)
            
            return SignatureInfo(
                algorithm="SHA256",
                timestamp=datetime.now(),
                certificate_subject="Developer ID Application",
                valid=(result.returncode == 0)
            )
            
        except FileNotFoundError:
            # Fallback if codesign not available
            return SignatureInfo(
                algorithm="SHA256",
                timestamp=datetime.now(),
                certificate_subject="Unknown",
                valid=False
            )
    
    def _verify_linux_signature(self, package_path: Path, signature_path: Path) -> SignatureInfo:
        """Verify Linux package signature
        
        Args:
            package_path: Path to signed package
            signature_path: Path to signature file
            
        Returns:
            SignatureInfo with verification results
        """
        try:
            # Use gpg to verify signature
            result = subprocess.run([
                "gpg", "--verify", str(signature_path), str(package_path)
            ], capture_output=True, text=True)
            
            return SignatureInfo(
                algorithm="SHA256",
                timestamp=datetime.now(),
                certificate_subject="TransRapport GPG Key",
                valid=(result.returncode == 0)
            )
            
        except FileNotFoundError:
            # Fallback if gpg not available
            return SignatureInfo(
                algorithm="SHA256",
                timestamp=datetime.now(),
                certificate_subject="Unknown",
                valid=False
            )
    
    def verify_signature(self, package_path: str, platform: Platform) -> Optional[SignatureInfo]:
        """Verify signature of a signed package
        
        Args:
            package_path: Path to package file
            platform: Target platform
            
        Returns:
            SignatureInfo if signature found, None otherwise
        """
        package_file = Path(package_path)
        
        if not package_file.exists():
            return None
        
        if platform == Platform.WINDOWS_11:
            return self._verify_windows_signature(package_file)
        elif platform == Platform.MACOS:
            return self._verify_macos_signature(package_file)
        else:  # Linux platforms
            signature_file = Path(str(package_file) + ".sig")
            if signature_file.exists():
                return self._verify_linux_signature(package_file, signature_file)
        
        return None