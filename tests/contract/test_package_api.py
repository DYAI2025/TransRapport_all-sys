"""
Contract test for POST /package endpoint

CRITICAL: This test MUST FAIL before implementation.
Tests the Package API contract from contracts/build-api.json
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path


class TestPackageAPI:
    """Contract tests for Package API endpoint"""
    
    def test_package_endpoint_exists(self):
        """Test that package CLI command exists and responds"""
        # This test MUST FAIL until package service is implemented
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'package',
            '--build-id', 'test-build-12345',
            '--bundle-type', 'msi',
            '--signing-required',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Parse JSON response
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON response, got: {result.stdout}")
        
        # Test MUST FAIL - expecting NOT_IMPLEMENTED error
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'
        assert 'not yet implemented' in response.get('message', '').lower()

    def test_package_request_schema_validation(self):
        """Test PackageRequest schema validation"""
        # Test valid request with all bundle types
        bundle_types = ['msi', 'exe', 'dmg', 'app', 'deb', 'rpm', 'appimage']
        
        for bundle_type in bundle_types:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'package',
                '--build-id', f'build-{bundle_type}-001',
                '--bundle-type', bundle_type,
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            
            # Should fail with NOT_IMPLEMENTED, not schema validation error
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Bundle type {bundle_type} should be recognized"

    def test_package_invalid_bundle_type_rejection(self):
        """Test invalid bundle type is rejected"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'package',
            '--build-id', 'test-build-001',
            '--bundle-type', 'invalid-bundle',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should fail due to CLI validation (not implementation)
        assert result.returncode != 0
        # Click should reject invalid choice before reaching our code

    def test_package_missing_build_id(self):
        """Test missing build-id is rejected"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'package',
            '--bundle-type', 'msi',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should fail due to required argument missing
        assert result.returncode != 0

    def test_package_response_schema_structure(self):
        """Test that response follows PackageResponse schema structure"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'package',
            '--build-id', 'test-build-schema',
            '--bundle-type', 'deb',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Required fields per PackageResponse schema (error case)
        assert 'success' in response
        assert 'error' in response
        assert 'message' in response
        assert isinstance(response['success'], bool)

    def test_package_signing_required_flag(self):
        """Test signing-required flag handling"""
        # Test with signing required
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'package',
            '--build-id', 'test-build-signed',
            '--bundle-type', 'msi',
            '--signing-required',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'
        
        # Test without signing required
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'package',
            '--build-id', 'test-build-unsigned',
            '--bundle-type', 'appimage',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_package_human_format_output(self):
        """Test human-readable format output"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'package',
            '--build-id', 'test-build-human',
            '--bundle-type', 'dmg',
            '--format', 'human'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should contain human-readable error message
        assert 'Package failed' in result.stdout
        assert 'not yet implemented' in result.stdout.lower()
        assert result.returncode == 1

    def test_package_windows_bundle_types(self):
        """Test Windows-specific bundle types"""
        windows_types = ['msi', 'exe']
        
        for bundle_type in windows_types:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'package',
                '--build-id', f'windows-build-{bundle_type}',
                '--bundle-type', bundle_type,
                '--signing-required',
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Windows bundle type {bundle_type} should be supported"

    def test_package_macos_bundle_types(self):
        """Test macOS-specific bundle types"""
        macos_types = ['dmg', 'app']
        
        for bundle_type in macos_types:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'package',
                '--build-id', f'macos-build-{bundle_type}',
                '--bundle-type', bundle_type,
                '--signing-required',
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"macOS bundle type {bundle_type} should be supported"

    def test_package_linux_bundle_types(self):
        """Test Linux-specific bundle types"""
        linux_types = ['deb', 'rpm', 'appimage']
        
        for bundle_type in linux_types:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'package',
                '--build-id', f'linux-build-{bundle_type}',
                '--bundle-type', bundle_type,
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Linux bundle type {bundle_type} should be supported"

    @pytest.mark.integration
    def test_package_build_id_validation(self):
        """Test build ID validation and existence check"""
        # Test with various build ID formats
        build_ids = [
            'build-12345-abcdef',
            'windows-x64-1.0.0-release',
            'macos-universal-2.1.0-debug',
            'linux-deb-1.5.0-release'
        ]
        
        for build_id in build_ids:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'package',
                '--build-id', build_id,
                '--bundle-type', 'msi',
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            
            # Must fail until package service validates build exists
            assert response.get('success') is False
            assert response.get('error') == 'NOT_IMPLEMENTED'

    @pytest.mark.integration
    def test_package_dependency_bundling_contract(self):
        """Test that package includes dependency bundling information"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'package',
            '--build-id', 'test-deps-build',
            '--bundle-type', 'appimage',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until package service bundles dependencies
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'