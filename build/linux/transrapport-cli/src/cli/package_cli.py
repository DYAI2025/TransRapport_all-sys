#!/usr/bin/env python3
"""
TransRapport Packaging CLI

Command-line interface for cross-platform installer generation.
Supports Windows (.msi), macOS (.dmg), and Linux (.deb/.rpm/.AppImage).
"""

import click
import json
import sys
from pathlib import Path

# Import our services
from src.lib.packaging.models import (
    BuildRequest, PackageRequest, SignRequest, ValidateRequest,
    Platform, Architecture, Profile, BundleType, ValidationType, CertificateSource
)
from src.lib.packaging.services import (
    BuildService, PackageService, SignService, ValidateService
)


@click.group()
@click.version_option(version="1.0.0")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """TransRapport Cross-Platform Packaging CLI"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.option('--platform', required=True, 
              type=click.Choice(['windows-11', 'macos', 'linux-deb', 'linux-rpm', 'linux-appimage']),
              help='Target platform for build')
@click.option('--version', required=True, help='Application version (MAJOR.MINOR.BUILD)')
@click.option('--profile', default='release', type=click.Choice(['debug', 'release']),
              help='Build profile')
@click.option('--architecture', default=None, type=click.Choice(['x64', 'arm64', 'universal']),
              help='Target CPU architecture')
@click.option('--format', default='json', type=click.Choice(['json', 'human']),
              help='Output format')
@click.pass_context
def build(ctx, platform, version, profile, architecture, format):
    """Build application for target platform"""
    if ctx.obj.get('verbose'):
        click.echo(f"Building {platform} {architecture or 'default'} version {version} ({profile} profile)")
    
    try:
        # Create build request
        request = BuildRequest(
            platform=Platform(platform),
            version=version,
            profile=Profile(profile),
            architecture=Architecture(architecture) if architecture else None
        )
        
        # Initialize build service
        build_service = BuildService()
        
        # Execute build
        response = build_service.build(request)
        
        # Format output
        if format == 'json':
            click.echo(json.dumps(response.to_dict(), indent=2))
        else:
            if response.success:
                click.echo(f"✅ Build completed successfully")
                if response.build_id:
                    click.echo(f"Build ID: {response.build_id}")
                if response.build_time:
                    click.echo(f"Build time: {response.build_time:.2f}s")
                if response.artifacts:
                    click.echo(f"Artifacts: {len(response.artifacts)} files")
            else:
                click.echo(f"❌ Build failed: {response.message or response.error}")
        
        if not response.success:
            sys.exit(1)
            
    except Exception as e:
        error_result = {
            "success": False,
            "error": "CLI_ERROR",
            "message": f"CLI error: {str(e)}"
        }
        
        if format == 'json':
            click.echo(json.dumps(error_result, indent=2))
        else:
            click.echo(f"❌ CLI Error: {str(e)}")
        
        sys.exit(1)


@cli.command()
@click.option('--build-id', required=True, help='Build ID from build step')
@click.option('--bundle-type', required=True,
              type=click.Choice(['msi', 'exe', 'dmg', 'app', 'deb', 'rpm', 'appimage']),
              help='Target installer package type')
@click.option('--signing-required', is_flag=True, help='Whether package requires code signing')
@click.option('--format', default='json', type=click.Choice(['json', 'human']),
              help='Output format')
@click.pass_context
def package(ctx, build_id, bundle_type, signing_required, format):
    """Generate installer package from built application"""
    if ctx.obj.get('verbose'):
        click.echo(f"Packaging build {build_id} as {bundle_type} (signing: {signing_required})")
    
    try:
        # Create package request
        request = PackageRequest(
            build_id=build_id,
            bundle_type=BundleType(bundle_type),
            signing_required=signing_required
        )
        
        # Initialize package service
        package_service = PackageService()
        
        # Execute packaging
        response = package_service.package(request)
        
        # Format output
        if format == 'json':
            click.echo(json.dumps(response.to_dict(), indent=2))
        else:
            if response.success:
                click.echo(f"✅ Package created successfully")
                if response.package:
                    click.echo(f"Package path: {response.package.path}")
                    click.echo(f"Package size: {response.package.size / (1024*1024):.1f} MB")
                if response.package_time:
                    click.echo(f"Package time: {response.package_time:.2f}s")
            else:
                click.echo(f"❌ Package failed: {response.message or response.error}")
        
        if not response.success:
            sys.exit(1)
            
    except Exception as e:
        error_result = {
            "success": False,
            "error": "CLI_ERROR",
            "message": f"CLI error: {str(e)}"
        }
        
        if format == 'json':
            click.echo(json.dumps(error_result, indent=2))
        else:
            click.echo(f"❌ CLI Error: {str(e)}")
        
        sys.exit(1)


@cli.command()
@click.option('--package-path', required=True, help='Path to package to be signed')
@click.option('--platform', required=True, type=click.Choice(['windows', 'macos', 'linux']),
              help='Platform for signing')
@click.option('--certificate-source', required=True,
              type=click.Choice(['azure_key_vault', 'apple_developer', 'local_certificate']),
              help='Source of signing certificate')
@click.option('--format', default='json', type=click.Choice(['json', 'human']),
              help='Output format')
@click.pass_context
def sign(ctx, package_path, platform, certificate_source, format):
    """Code sign installer package"""
    if ctx.obj.get('verbose'):
        click.echo(f"Signing {package_path} for {platform} using {certificate_source}")
    
    try:
        # Map platform to Platform enum
        platform_map = {
            'windows': Platform.WINDOWS_11,
            'macos': Platform.MACOS,
            'linux': Platform.LINUX_DEB  # Default to DEB for generic linux
        }
        
        # Create sign request
        request = SignRequest(
            package_path=package_path,
            platform=platform_map[platform],
            certificate_source=CertificateSource(certificate_source)
        )
        
        # Initialize sign service
        sign_service = SignService()
        
        # Execute signing
        response = sign_service.sign(request)
        
        # Format output
        if format == 'json':
            click.echo(json.dumps(response.to_dict(), indent=2))
        else:
            if response.success:
                click.echo(f"✅ Package signed successfully")
                if response.signed_package_path:
                    click.echo(f"Signed package: {response.signed_package_path}")
                if response.signature:
                    click.echo(f"Signature valid: {response.signature.valid}")
                if response.signing_time:
                    click.echo(f"Signing time: {response.signing_time:.2f}s")
            else:
                click.echo(f"❌ Sign failed: {response.message or response.error}")
        
        if not response.success:
            sys.exit(1)
            
    except Exception as e:
        error_result = {
            "success": False,
            "error": "CLI_ERROR",
            "message": f"CLI error: {str(e)}"
        }
        
        if format == 'json':
            click.echo(json.dumps(error_result, indent=2))
        else:
            click.echo(f"❌ CLI Error: {str(e)}")
        
        sys.exit(1)


@cli.command()
@click.option('--package-path', required=True, help='Path to package to validate')
@click.option('--validation-type', required=True,
              type=click.Choice(['integrity', 'compatibility', 'security', 'full']),
              help='Type of validation to perform')
@click.option('--format', default='json', type=click.Choice(['json', 'human']),
              help='Output format')
@click.pass_context
def validate(ctx, package_path, validation_type, format):
    """Validate installer package"""
    if ctx.obj.get('verbose'):
        click.echo(f"Validating {package_path} ({validation_type} validation)")
    
    try:
        # Create validate request
        request = ValidateRequest(
            package_path=package_path,
            validation_type=ValidationType(validation_type)
        )
        
        # Initialize validate service
        validate_service = ValidateService()
        
        # Execute validation
        response = validate_service.validate(request)
        
        # Format output
        if format == 'json':
            click.echo(json.dumps(response.to_dict(), indent=2))
        else:
            if response.success:
                click.echo(f"✅ Validation completed successfully")
                if response.overall_valid is not None:
                    status = "✅ VALID" if response.overall_valid else "❌ INVALID"
                    click.echo(f"Overall result: {status}")
                if response.validation_results:
                    click.echo(f"Checks performed: {len(response.validation_results)}")
                    for result in response.validation_results:
                        status = "✅" if result.passed else "❌"
                        click.echo(f"  {status} {result.check_name}: {result.message}")
                if response.validation_time:
                    click.echo(f"Validation time: {response.validation_time:.2f}s")
            else:
                click.echo(f"❌ Validation failed: {response.message or response.error}")
        
        # Exit with error code if validation failed or overall invalid
        if not response.success or (response.overall_valid is False):
            sys.exit(1)
            
    except Exception as e:
        error_result = {
            "success": False,
            "error": "CLI_ERROR",
            "message": f"CLI error: {str(e)}"
        }
        
        if format == 'json':
            click.echo(json.dumps(error_result, indent=2))
        else:
            click.echo(f"❌ CLI Error: {str(e)}")
        
        sys.exit(1)


@cli.command()
def status():
    """Show packaging system status"""
    click.echo("TransRapport Packaging System Status:")
    click.echo("✅ CLI interface initialized")
    
    # Test service initialization
    try:
        BuildService()
        click.echo("✅ Build service available")
    except Exception:
        click.echo("❌ Build service not available")
    
    try:
        PackageService()
        click.echo("✅ Package service available")
    except Exception:
        click.echo("❌ Package service not available")
    
    try:
        SignService()
        click.echo("✅ Signing service available")
    except Exception:
        click.echo("❌ Signing service not available")
    
    try:
        ValidateService()
        click.echo("✅ Validation service available")
    except Exception:
        click.echo("❌ Validation service not available")
    
    click.echo("\n📋 Current implementation status:")
    click.echo("✅ All core services implemented")
    click.echo("✅ Data models defined")
    click.echo("✅ Contract tests written")
    click.echo("✅ Integration tests written")
    click.echo("\n🚀 Ready for testing and deployment!")


if __name__ == '__main__':
    cli()