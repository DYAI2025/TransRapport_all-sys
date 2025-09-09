"""
TransRapport Cross-Platform Packaging Library

Provides cross-platform installer generation for Windows (.msi), 
macOS (.dmg), and Linux (.deb/.rpm/.AppImage) with code signing support.
"""

__version__ = "1.0.0"
__all__ = [
    "BuildService",
    "PackageService", 
    "SigningService",
    "ValidationService",
    "InstallationPackage",
    "BuildConfiguration",
    "InstallationSession",
    "SystemRegistryEntry"
]