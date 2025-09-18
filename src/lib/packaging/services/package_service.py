"""
Package service implementation

Handles packaging of built artifacts into distribution-ready formats.
Manages bundle creation, metadata generation, and package optimization.
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models import (
    PackageRequest, PackageResponse, PackageInfo, BundleType, Platform,
    create_error_response
)


logger = logging.getLogger(__name__)


class PackageService:
    """Service for packaging build artifacts into distribution formats"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize package service
        
        Args:
            project_root: Root directory of the project. If None, auto-detect.
        """
        self.project_root = project_root or self._detect_project_root()
        self.desktop_dir = self.project_root / "desktop"
        self.tauri_dir = self.desktop_dir / "src-tauri"
        self.build_cache = {}  # In-memory cache for build metadata
        
        # Load application metadata
        self.app_metadata = self._load_app_metadata()
    
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
    
    def _load_app_metadata(self) -> Dict:
        """Load application metadata from Tauri config"""
        config_path = self.tauri_dir / "tauri.conf.json"
        
        if not config_path.exists():
            logger.warning(f"Tauri config not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('package', {})
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Failed to load app metadata: {e}")
            return {}
    
    def package(self, request: PackageRequest) -> PackageResponse:
        """Package build artifacts into distribution format

        Args:
            request: Package request parameters

        Returns:
            PackageResponse with packaging results
        """
        logger.info(
            "Packaging requested for build %s (%s) – service not yet implemented",
            request.build_id,
            request.bundle_type.value,
        )

        return create_error_response(
            PackageResponse,
            "NOT_IMPLEMENTED",
            "Package service not yet implemented for offline packaging pipeline.",
        )
    
    def _validate_package_request(self, request: PackageRequest) -> Optional[str]:
        """Validate package request parameters
        
        Args:
            request: Package request to validate
            
        Returns:
            Error message if invalid, None if valid
        """
        # Validate build ID format
        if not request.build_id or len(request.build_id.strip()) == 0:
            return "Build ID is required"
        
        # Validate bundle type support
        supported_bundles = [
            BundleType.MSI, BundleType.EXE, BundleType.DMG, BundleType.APP,
            BundleType.DEB, BundleType.RPM, BundleType.APPIMAGE
        ]
        if request.bundle_type not in supported_bundles:
            return f"Unsupported bundle type: {request.bundle_type.value}"
        
        return None
    
    def _resolve_build_artifacts(self, build_id: str) -> Optional[Dict]:
        """Resolve build artifacts from build ID
        
        Args:
            build_id: Build identifier
            
        Returns:
            Build information dictionary or None if not found
        """
        # In a full implementation, this would query a build database
        # For now, we'll look for artifacts in the target directory
        
        # Check cache first
        if build_id in self.build_cache:
            return self.build_cache[build_id]
        
        # Look for build artifacts in target directory
        target_dir = self.tauri_dir / "target"
        
        if not target_dir.exists():
            return None
        
        # Search for artifacts in release and debug directories
        for profile in ["release", "debug"]:
            profile_dir = target_dir / profile
            bundle_dir = profile_dir / "bundle"
            
            if bundle_dir.exists():
                # Found build artifacts
                build_info = {
                    "build_id": build_id,
                    "profile": profile,
                    "artifacts_dir": bundle_dir,
                    "timestamp": bundle_dir.stat().st_mtime
                }
                
                # Cache the result
                self.build_cache[build_id] = build_info
                return build_info
        
        return None
    
    def _create_package(self, request: PackageRequest, build_info: Dict) -> PackageResponse:
        """Create package from build artifacts
        
        Args:
            request: Package request
            build_info: Build information
            
        Returns:
            PackageResponse with packaging results
        """
        artifacts_dir = build_info["artifacts_dir"]
        
        if request.bundle_type == BundleType.MSI:
            return self._create_msi_package(request, artifacts_dir)
        elif request.bundle_type == BundleType.EXE:
            return self._create_exe_package(request, artifacts_dir)
        elif request.bundle_type == BundleType.DMG:
            return self._create_dmg_package(request, artifacts_dir)
        elif request.bundle_type == BundleType.APP:
            return self._create_app_package(request, artifacts_dir)
        elif request.bundle_type == BundleType.DEB:
            return self._create_deb_package(request, artifacts_dir)
        elif request.bundle_type == BundleType.RPM:
            return self._create_rpm_package(request, artifacts_dir)
        elif request.bundle_type == BundleType.APPIMAGE:
            return self._create_appimage_package(request, artifacts_dir)
        else:
            return create_error_response(
                PackageResponse,
                "UNSUPPORTED_BUNDLE_TYPE",
                f"Bundle type {request.bundle_type.value} not implemented"
            )
    
    def _create_msi_package(self, request: PackageRequest, artifacts_dir: Path) -> PackageResponse:
        """Create MSI package for Windows
        
        Args:
            request: Package request
            artifacts_dir: Directory containing build artifacts
            
        Returns:
            PackageResponse with MSI package info
        """
        msi_dir = artifacts_dir / "msi"
        
        if not msi_dir.exists():
            return create_error_response(
                PackageResponse,
                "MSI_ARTIFACTS_NOT_FOUND",
                f"MSI artifacts not found in {artifacts_dir}"
            )
        
        # Find MSI file
        msi_files = list(msi_dir.glob("*.msi"))
        if not msi_files:
            return create_error_response(
                PackageResponse,
                "MSI_FILE_NOT_FOUND",
                "No MSI files found in artifacts directory"
            )
        
        msi_file = msi_files[0]  # Take first MSI file
        
        # Create package info
        package_info = PackageInfo(
            path=str(msi_file),
            size=msi_file.stat().st_size,
            checksum=self._calculate_checksum(msi_file),
            bundle_type=BundleType.MSI,
            signed=False  # Will be updated by signing service
        )
        
        return PackageResponse(
            success=True,
            package=package_info
        )
    
    def _create_exe_package(self, request: PackageRequest, artifacts_dir: Path) -> PackageResponse:
        """Create EXE package (NSIS) for Windows"""
        nsis_dir = artifacts_dir / "nsis"
        
        if not nsis_dir.exists():
            return create_error_response(
                PackageResponse,
                "EXE_ARTIFACTS_NOT_FOUND",
                f"NSIS artifacts not found in {artifacts_dir}"
            )
        
        # Find EXE file
        exe_files = list(nsis_dir.glob("*.exe"))
        if not exe_files:
            return create_error_response(
                PackageResponse,
                "EXE_FILE_NOT_FOUND",
                "No EXE files found in artifacts directory"
            )
        
        exe_file = exe_files[0]
        
        package_info = PackageInfo(
            path=str(exe_file),
            size=exe_file.stat().st_size,
            checksum=self._calculate_checksum(exe_file),
            bundle_type=BundleType.EXE,
            signed=False
        )
        
        return PackageResponse(
            success=True,
            package=package_info
        )
    
    def _create_dmg_package(self, request: PackageRequest, artifacts_dir: Path) -> PackageResponse:
        """Create DMG package for macOS"""
        dmg_dir = artifacts_dir / "dmg"
        
        if not dmg_dir.exists():
            return create_error_response(
                PackageResponse,
                "DMG_ARTIFACTS_NOT_FOUND",
                f"DMG artifacts not found in {artifacts_dir}"
            )
        
        # Find DMG file
        dmg_files = list(dmg_dir.glob("*.dmg"))
        if not dmg_files:
            return create_error_response(
                PackageResponse,
                "DMG_FILE_NOT_FOUND",
                "No DMG files found in artifacts directory"
            )
        
        dmg_file = dmg_files[0]
        
        package_info = PackageInfo(
            path=str(dmg_file),
            size=dmg_file.stat().st_size,
            checksum=self._calculate_checksum(dmg_file),
            bundle_type=BundleType.DMG,
            signed=False
        )
        
        return PackageResponse(
            success=True,
            package=package_info
        )
    
    def _create_app_package(self, request: PackageRequest, artifacts_dir: Path) -> PackageResponse:
        """Create APP bundle package for macOS"""
        macos_dir = artifacts_dir / "macos"
        
        if not macos_dir.exists():
            return create_error_response(
                PackageResponse,
                "APP_ARTIFACTS_NOT_FOUND",
                f"macOS app artifacts not found in {artifacts_dir}"
            )
        
        # Find .app bundle
        app_bundles = list(macos_dir.glob("*.app"))
        if not app_bundles:
            return create_error_response(
                PackageResponse,
                "APP_BUNDLE_NOT_FOUND",
                "No .app bundles found in artifacts directory"
            )
        
        app_bundle = app_bundles[0]
        
        # Calculate bundle size (recursive)
        bundle_size = sum(f.stat().st_size for f in app_bundle.rglob("*") if f.is_file())
        
        package_info = PackageInfo(
            path=str(app_bundle),
            size=bundle_size,
            checksum=self._calculate_directory_checksum(app_bundle),
            bundle_type=BundleType.APP,
            signed=False
        )
        
        return PackageResponse(
            success=True,
            package=package_info
        )
    
    def _create_deb_package(self, request: PackageRequest, artifacts_dir: Path) -> PackageResponse:
        """Create DEB package for Debian/Ubuntu"""
        deb_dir = artifacts_dir / "deb"
        
        if not deb_dir.exists():
            return create_error_response(
                PackageResponse,
                "DEB_ARTIFACTS_NOT_FOUND",
                f"DEB artifacts not found in {artifacts_dir}"
            )
        
        # Find DEB file
        deb_files = list(deb_dir.glob("*.deb"))
        if not deb_files:
            return create_error_response(
                PackageResponse,
                "DEB_FILE_NOT_FOUND",
                "No DEB files found in artifacts directory"
            )
        
        deb_file = deb_files[0]
        
        package_info = PackageInfo(
            path=str(deb_file),
            size=deb_file.stat().st_size,
            checksum=self._calculate_checksum(deb_file),
            bundle_type=BundleType.DEB,
            signed=False
        )
        
        return PackageResponse(
            success=True,
            package=package_info
        )
    
    def _create_rpm_package(self, request: PackageRequest, artifacts_dir: Path) -> PackageResponse:
        """Create RPM package for Red Hat/Fedora"""
        rpm_dir = artifacts_dir / "rpm"
        
        if not rpm_dir.exists():
            return create_error_response(
                PackageResponse,
                "RPM_ARTIFACTS_NOT_FOUND",
                f"RPM artifacts not found in {artifacts_dir}"
            )
        
        # Find RPM file
        rpm_files = list(rpm_dir.glob("*.rpm"))
        if not rpm_files:
            return create_error_response(
                PackageResponse,
                "RPM_FILE_NOT_FOUND",
                "No RPM files found in artifacts directory"
            )
        
        rpm_file = rpm_files[0]
        
        package_info = PackageInfo(
            path=str(rpm_file),
            size=rpm_file.stat().st_size,
            checksum=self._calculate_checksum(rpm_file),
            bundle_type=BundleType.RPM,
            signed=False
        )
        
        return PackageResponse(
            success=True,
            package=package_info
        )
    
    def _create_appimage_package(self, request: PackageRequest, artifacts_dir: Path) -> PackageResponse:
        """Create AppImage package for Linux"""
        appimage_dir = artifacts_dir / "appimage"
        
        if not appimage_dir.exists():
            return create_error_response(
                PackageResponse,
                "APPIMAGE_ARTIFACTS_NOT_FOUND",
                f"AppImage artifacts not found in {artifacts_dir}"
            )
        
        # Find AppImage file
        appimage_files = list(appimage_dir.glob("*.AppImage"))
        if not appimage_files:
            return create_error_response(
                PackageResponse,
                "APPIMAGE_FILE_NOT_FOUND",
                "No AppImage files found in artifacts directory"
            )
        
        appimage_file = appimage_files[0]
        
        package_info = PackageInfo(
            path=str(appimage_file),
            size=appimage_file.stat().st_size,
            checksum=self._calculate_checksum(appimage_file),
            bundle_type=BundleType.APPIMAGE,
            signed=False
        )
        
        return PackageResponse(
            success=True,
            package=package_info
        )
    
    def _optimize_package(self, package_info: PackageInfo, request: PackageRequest) -> Optional[PackageInfo]:
        """Optimize package for distribution
        
        Args:
            package_info: Package information
            request: Package request
            
        Returns:
            Optimized package info or None if no optimization applied
        """
        # Package optimization strategies:
        # - Compress package contents
        # - Strip debug symbols for release builds
        # - Optimize bundle metadata
        # - Apply platform-specific optimizations
        
        # For now, return None indicating no optimization applied
        # This would be implemented based on specific optimization needs
        return None
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex-encoded SHA256 checksum
        """
        import hashlib
        
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _calculate_directory_checksum(self, dir_path: Path) -> str:
        """Calculate checksum of directory contents
        
        Args:
            dir_path: Path to directory
            
        Returns:
            Hex-encoded SHA256 checksum of all files in directory
        """
        import hashlib
        
        sha256_hash = hashlib.sha256()
        
        # Sort files for consistent hashing
        files = sorted(dir_path.rglob("*"))
        
        for file_path in files:
            if file_path.is_file():
                # Add relative path to hash
                rel_path = file_path.relative_to(dir_path)
                sha256_hash.update(str(rel_path).encode())
                
                # Add file contents to hash
                with open(file_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def get_package_metadata(self, package_path: str) -> Optional[Dict]:
        """Get metadata for a package
        
        Args:
            package_path: Path to package file
            
        Returns:
            Package metadata dictionary or None if not found
        """
        package_file = Path(package_path)
        
        if not package_file.exists():
            return None
        
        # Basic metadata
        metadata = {
            "path": str(package_file),
            "size": package_file.stat().st_size,
            "checksum": self._calculate_checksum(package_file),
            "modified_time": package_file.stat().st_mtime
        }
        
        # Add bundle type based on extension
        extension = package_file.suffix.lower()
        bundle_type_map = {
            ".msi": BundleType.MSI,
            ".exe": BundleType.EXE,
            ".dmg": BundleType.DMG,
            ".app": BundleType.APP,
            ".deb": BundleType.DEB,
            ".rpm": BundleType.RPM,
            ".appimage": BundleType.APPIMAGE
        }
        
        if extension in bundle_type_map:
            metadata["bundle_type"] = bundle_type_map[extension].value
        
        return metadata
    
    def cleanup_package_artifacts(self, build_id: str) -> bool:
        """Clean up packaging artifacts for a build
        
        Args:
            build_id: Build identifier
            
        Returns:
            True if cleanup successful, False otherwise
        """
        # Remove from cache
        if build_id in self.build_cache:
            del self.build_cache[build_id]
        
        # This would typically clean up temporary packaging files
        # For now, return True indicating basic cleanup
        return True