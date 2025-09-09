"""
Build service implementation

Handles cross-platform building using Tauri v2 framework.
Manages build configurations, dependency resolution, and artifact generation.
"""

import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from ..models import (
    BuildRequest, BuildResponse, BuildArtifact, Platform, Architecture, Profile,
    create_error_response
)


logger = logging.getLogger(__name__)


class BuildService:
    """Service for building TransRapport across platforms"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize build service
        
        Args:
            project_root: Root directory of the project. If None, auto-detect.
        """
        self.project_root = project_root or self._detect_project_root()
        self.desktop_dir = self.project_root / "desktop"
        self.tauri_dir = self.desktop_dir / "src-tauri"
        
        # Validate project structure
        if not self.desktop_dir.exists():
            raise ValueError(f"Desktop directory not found: {self.desktop_dir}")
        if not self.tauri_dir.exists():
            raise ValueError(f"Tauri directory not found: {self.tauri_dir}")
        
        # Load Tauri configuration
        self.tauri_config = self._load_tauri_config()
    
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
    
    def _load_tauri_config(self) -> Dict:
        """Load Tauri configuration"""
        config_path = self.tauri_dir / "tauri.conf.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Tauri config not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Tauri config JSON: {e}")
    
    def build(self, request: BuildRequest) -> BuildResponse:
        """Build the application for specified platform
        
        Args:
            request: Build request parameters
            
        Returns:
            BuildResponse with build results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting build for {request.platform.value} {request.version} {request.profile.value}")
            
            # Validate request
            validation_error = self._validate_build_request(request)
            if validation_error:
                return create_error_response(
                    BuildResponse,
                    "INVALID_REQUEST",
                    validation_error
                )
            
            # Set up build environment
            build_env = self._setup_build_environment(request)
            
            # Execute Tauri build
            build_result = self._execute_tauri_build(request, build_env)
            
            if not build_result.success:
                return build_result
            
            # Collect build artifacts
            artifacts = self._collect_build_artifacts(request)
            
            # Generate build ID
            build_id = self._generate_build_id(request)
            
            build_time = time.time() - start_time
            
            logger.info(f"Build completed successfully in {build_time:.2f}s")
            
            return BuildResponse(
                success=True,
                build_id=build_id,
                artifacts=artifacts,
                build_time=build_time
            )
            
        except Exception as e:
            logger.error(f"Build failed: {e}", exc_info=True)
            build_time = time.time() - start_time
            
            return BuildResponse(
                success=False,
                error="BUILD_FAILED",
                message=f"Build failed after {build_time:.2f}s: {str(e)}",
                build_time=build_time
            )
    
    def _validate_build_request(self, request: BuildRequest) -> Optional[str]:
        """Validate build request parameters
        
        Args:
            request: Build request to validate
            
        Returns:
            Error message if invalid, None if valid
        """
        # Validate version format
        if not self._is_valid_version(request.version):
            return f"Invalid version format: {request.version}. Expected semantic version (x.y.z)"
        
        # Validate platform support
        supported_platforms = [Platform.WINDOWS_11, Platform.MACOS, Platform.LINUX_DEB, 
                             Platform.LINUX_RPM, Platform.LINUX_APPIMAGE]
        if request.platform not in supported_platforms:
            return f"Unsupported platform: {request.platform.value}"
        
        # Validate architecture for platform
        if request.architecture:
            supported_archs = self._get_supported_architectures(request.platform)
            if request.architecture not in supported_archs:
                return f"Unsupported architecture {request.architecture.value} for platform {request.platform.value}"
        
        return None
    
    def _is_valid_version(self, version: str) -> bool:
        """Validate semantic version format"""
        import re
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-]+))?(?:\+([a-zA-Z0-9\-]+))?$'
        return bool(re.match(pattern, version))
    
    def _get_supported_architectures(self, platform: Platform) -> List[Architecture]:
        """Get supported architectures for platform"""
        platform_archs = {
            Platform.WINDOWS_11: [Architecture.X64, Architecture.ARM64],
            Platform.MACOS: [Architecture.X64, Architecture.ARM64, Architecture.UNIVERSAL],
            Platform.LINUX_DEB: [Architecture.X64, Architecture.ARM64],
            Platform.LINUX_RPM: [Architecture.X64, Architecture.ARM64],
            Platform.LINUX_APPIMAGE: [Architecture.X64, Architecture.ARM64]
        }
        
        return platform_archs.get(platform, [Architecture.X64])
    
    def _setup_build_environment(self, request: BuildRequest) -> Dict[str, str]:
        """Set up environment variables for build
        
        Args:
            request: Build request
            
        Returns:
            Dictionary of environment variables
        """
        env = os.environ.copy()
        
        # Set version
        env['TAURI_APP_VERSION'] = request.version
        
        # Set build profile
        if request.profile == Profile.DEBUG:
            env['TAURI_BUILD_DEBUG'] = '1'
        else:
            env['TAURI_BUILD_RELEASE'] = '1'
        
        # Set architecture if specified
        if request.architecture:
            env['TAURI_TARGET_ARCH'] = request.architecture.value
        
        # Platform-specific environment setup
        if request.platform == Platform.WINDOWS_11:
            env['TAURI_PLATFORM'] = 'windows'
            env['TAURI_BUNDLE_WINDOWS_MSI'] = '1'
        elif request.platform == Platform.MACOS:
            env['TAURI_PLATFORM'] = 'macos'
            env['TAURI_BUNDLE_MACOS_DMG'] = '1'
        elif request.platform in [Platform.LINUX_DEB, Platform.LINUX_RPM, Platform.LINUX_APPIMAGE]:
            env['TAURI_PLATFORM'] = 'linux'
            if request.platform == Platform.LINUX_DEB:
                env['TAURI_BUNDLE_LINUX_DEB'] = '1'
            elif request.platform == Platform.LINUX_RPM:
                env['TAURI_BUNDLE_LINUX_RPM'] = '1'
            elif request.platform == Platform.LINUX_APPIMAGE:
                env['TAURI_BUNDLE_LINUX_APPIMAGE'] = '1'
        
        return env
    
    def _execute_tauri_build(self, request: BuildRequest, env: Dict[str, str]) -> BuildResponse:
        """Execute Tauri build command
        
        Args:
            request: Build request
            env: Environment variables
            
        Returns:
            BuildResponse indicating build success/failure
        """
        # Construct Tauri build command
        cmd = ['npm', 'run', 'tauri', 'build']
        
        # Add debug flag if debug profile
        if request.profile == Profile.DEBUG:
            cmd.append('--debug')
        
        # Add target specification if architecture specified
        if request.architecture:
            target = self._get_rust_target(request.platform, request.architecture)
            if target:
                cmd.extend(['--target', target])
        
        logger.info(f"Executing build command: {' '.join(cmd)}")
        
        try:
            # Execute build in desktop directory
            result = subprocess.run(
                cmd,
                cwd=self.desktop_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("Tauri build completed successfully")
                return BuildResponse(success=True)
            else:
                logger.error(f"Tauri build failed with code {result.returncode}")
                logger.error(f"Stderr: {result.stderr}")
                
                return create_error_response(
                    BuildResponse,
                    "TAURI_BUILD_FAILED",
                    f"Tauri build failed: {result.stderr}"
                )
                
        except subprocess.TimeoutExpired:
            return create_error_response(
                BuildResponse,
                "BUILD_TIMEOUT",
                "Build timed out after 30 minutes"
            )
        except FileNotFoundError:
            return create_error_response(
                BuildResponse,
                "TAURI_NOT_FOUND",
                "Tauri CLI not found. Ensure npm dependencies are installed."
            )
    
    def _get_rust_target(self, platform: Platform, architecture: Architecture) -> Optional[str]:
        """Get Rust target triple for platform and architecture
        
        Args:
            platform: Target platform
            architecture: Target architecture
            
        Returns:
            Rust target triple or None if default
        """
        targets = {
            (Platform.WINDOWS_11, Architecture.X64): "x86_64-pc-windows-msvc",
            (Platform.WINDOWS_11, Architecture.ARM64): "aarch64-pc-windows-msvc",
            (Platform.MACOS, Architecture.X64): "x86_64-apple-darwin",
            (Platform.MACOS, Architecture.ARM64): "aarch64-apple-darwin",
            (Platform.LINUX_DEB, Architecture.X64): "x86_64-unknown-linux-gnu",
            (Platform.LINUX_DEB, Architecture.ARM64): "aarch64-unknown-linux-gnu",
            (Platform.LINUX_RPM, Architecture.X64): "x86_64-unknown-linux-gnu",
            (Platform.LINUX_RPM, Architecture.ARM64): "aarch64-unknown-linux-gnu",
            (Platform.LINUX_APPIMAGE, Architecture.X64): "x86_64-unknown-linux-gnu",
            (Platform.LINUX_APPIMAGE, Architecture.ARM64): "aarch64-unknown-linux-gnu",
        }
        
        return targets.get((platform, architecture))
    
    def _collect_build_artifacts(self, request: BuildRequest) -> List[BuildArtifact]:
        """Collect build artifacts from target directory
        
        Args:
            request: Build request
            
        Returns:
            List of build artifacts
        """
        artifacts = []
        
        # Determine target directory based on profile
        profile_dir = "debug" if request.profile == Profile.DEBUG else "release"
        target_dir = self.tauri_dir / "target" / profile_dir
        
        # Look for bundle directory
        bundle_dir = target_dir / "bundle"
        
        if not bundle_dir.exists():
            logger.warning(f"Bundle directory not found: {bundle_dir}")
            return artifacts
        
        # Collect artifacts based on platform
        if request.platform == Platform.WINDOWS_11:
            # Look for MSI and EXE files
            msi_dir = bundle_dir / "msi"
            nsis_dir = bundle_dir / "nsis"
            
            for artifact_dir in [msi_dir, nsis_dir]:
                if artifact_dir.exists():
                    for file_path in artifact_dir.glob("*"):
                        if file_path.is_file():
                            artifact = self._create_artifact(file_path, request.architecture)
                            if artifact:
                                artifacts.append(artifact)
        
        elif request.platform == Platform.MACOS:
            # Look for DMG and APP files
            dmg_dir = bundle_dir / "dmg"
            macos_dir = bundle_dir / "macos"
            
            for artifact_dir in [dmg_dir, macos_dir]:
                if artifact_dir.exists():
                    for file_path in artifact_dir.glob("*"):
                        if file_path.is_file() or (file_path.is_dir() and file_path.suffix == ".app"):
                            artifact = self._create_artifact(file_path, request.architecture)
                            if artifact:
                                artifacts.append(artifact)
        
        else:  # Linux platforms
            # Look for DEB, RPM, AppImage files
            for bundle_type in ["deb", "rpm", "appimage"]:
                type_dir = bundle_dir / bundle_type
                if type_dir.exists():
                    for file_path in type_dir.glob("*"):
                        if file_path.is_file():
                            artifact = self._create_artifact(file_path, request.architecture)
                            if artifact:
                                artifacts.append(artifact)
        
        return artifacts
    
    def _create_artifact(self, file_path: Path, architecture: Optional[Architecture]) -> Optional[BuildArtifact]:
        """Create build artifact from file
        
        Args:
            file_path: Path to artifact file
            architecture: Target architecture
            
        Returns:
            BuildArtifact or None if file doesn't exist
        """
        if not file_path.exists():
            return None
        
        try:
            # Calculate file size
            size = file_path.stat().st_size
            
            # Calculate checksum
            checksum = self._calculate_checksum(file_path)
            
            # Default architecture if not specified
            if not architecture:
                architecture = Architecture.X64
            
            return BuildArtifact(
                path=str(file_path),
                size=size,
                checksum=checksum,
                architecture=architecture
            )
            
        except Exception as e:
            logger.warning(f"Failed to create artifact for {file_path}: {e}")
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
    
    def _generate_build_id(self, request: BuildRequest) -> str:
        """Generate unique build ID
        
        Args:
            request: Build request
            
        Returns:
            Unique build identifier
        """
        import uuid
        from datetime import datetime
        
        # Create build ID with timestamp and platform info
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        platform_arch = f"{request.platform.value}_{request.architecture.value if request.architecture else 'default'}"
        unique_id = str(uuid.uuid4())[:8]
        
        return f"build_{timestamp}_{platform_arch}_{unique_id}"
    
    def get_build_status(self, build_id: str) -> Optional[Dict]:
        """Get status of a build by ID
        
        Args:
            build_id: Build identifier
            
        Returns:
            Build status information or None if not found
        """
        # This would typically query a build database
        # For now, return None indicating build tracking not implemented
        return None
    
    def cleanup_build_artifacts(self, build_id: str) -> bool:
        """Clean up artifacts for a build
        
        Args:
            build_id: Build identifier
            
        Returns:
            True if cleanup successful, False otherwise
        """
        # This would typically clean up temporary files and artifacts
        # For now, return True indicating basic cleanup
        return True