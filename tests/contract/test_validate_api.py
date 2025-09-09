"""
Contract test for POST /validate endpoint

CRITICAL: This test MUST FAIL before implementation.
Tests the Validate API contract from contracts/build-api.json
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path


class TestValidateAPI:
    """Contract tests for Validate API endpoint"""
    
    def test_validate_endpoint_exists(self):
        """Test that validate CLI command exists and responds"""
        # This test MUST FAIL until validate service is implemented
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.msi',
            '--validation-type', 'full',
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

    def test_validate_request_schema_validation(self):
        """Test ValidateRequest schema validation"""
        # Test all valid validation types
        validation_types = ['integrity', 'compatibility', 'security', 'full']
        
        for validation_type in validation_types:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'validate',
                '--package-path', f'/fake/path/installer-{validation_type}.deb',
                '--validation-type', validation_type,
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            
            # Should fail with NOT_IMPLEMENTED, not schema validation error
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Validation type {validation_type} should be recognized"

    def test_validate_invalid_validation_type_rejection(self):
        """Test invalid validation type is rejected"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.dmg',
            '--validation-type', 'invalid-validation',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should fail due to CLI validation (not implementation)
        assert result.returncode != 0

    def test_validate_missing_required_fields(self):
        """Test missing required fields are rejected"""
        # Missing package-path
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--validation-type', 'integrity',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        assert result.returncode != 0
        
        # Missing validation-type
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.rpm',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        assert result.returncode != 0

    def test_validate_response_schema_structure(self):
        """Test that response follows ValidateResponse schema structure"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.AppImage',
            '--validation-type', 'security',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Required fields per ValidateResponse schema (error case)
        assert 'success' in response
        assert 'error' in response
        assert 'message' in response
        assert isinstance(response['success'], bool)

    def test_validate_integrity_validation(self):
        """Test integrity validation type"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.msi',
            '--validation-type', 'integrity',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_validate_compatibility_validation(self):
        """Test compatibility validation type"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.dmg',
            '--validation-type', 'compatibility',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_validate_security_validation(self):
        """Test security validation type"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.deb',
            '--validation-type', 'security',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_validate_full_validation(self):
        """Test full validation type (includes all checks)"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.rpm',
            '--validation-type', 'full',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_validate_human_format_output(self):
        """Test human-readable format output"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.AppImage',
            '--validation-type', 'full',
            '--format', 'human'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should contain human-readable error message
        assert 'Validation failed' in result.stdout
        assert 'not yet implemented' in result.stdout.lower()
        assert result.returncode == 1

    def test_validate_windows_package_types(self):
        """Test validation of Windows package types"""
        windows_packages = [
            '/fake/path/TransRapport.msi',
            '/fake/path/TransRapport.exe'
        ]
        
        for package_path in windows_packages:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'validate',
                '--package-path', package_path,
                '--validation-type', 'security',
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Windows package {package_path} should be supported"

    def test_validate_macos_package_types(self):
        """Test validation of macOS package types"""
        macos_packages = [
            '/fake/path/TransRapport.dmg',
            '/fake/path/TransRapport.app'
        ]
        
        for package_path in macos_packages:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'validate',
                '--package-path', package_path,
                '--validation-type', 'security',
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"macOS package {package_path} should be supported"

    def test_validate_linux_package_types(self):
        """Test validation of Linux package types"""
        linux_packages = [
            '/fake/path/transrapport.deb',
            '/fake/path/transrapport.rpm',
            '/fake/path/TransRapport.AppImage'
        ]
        
        for package_path in linux_packages:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'validate',
                '--package-path', package_path,
                '--validation-type', 'integrity',
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Linux package {package_path} should be supported"

    @pytest.mark.integration
    def test_validate_package_existence_check(self):
        """Test that validation checks if package file exists"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/nonexistent/path/installer.msi',
            '--validation-type', 'integrity',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until validate service checks file existence
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'

    @pytest.mark.integration
    def test_validate_signature_verification(self):
        """Test signature validation functionality"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/signed-installer.dmg',
            '--validation-type', 'security',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until validate service verifies signatures
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'

    @pytest.mark.integration
    def test_validate_compatibility_matrix(self):
        """Test compatibility validation against target systems"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.deb',
            '--validation-type', 'compatibility',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until validate service checks OS compatibility
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'

    @pytest.mark.integration 
    def test_validate_integrity_checksums(self):
        """Test integrity validation with checksums"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.rpm',
            '--validation-type', 'integrity',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until validate service computes and verifies checksums
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'

    @pytest.mark.integration
    def test_validate_full_validation_comprehensive(self):
        """Test full validation runs all validation types"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'validate',
            '--package-path', '/fake/path/installer.AppImage',
            '--validation-type', 'full',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until validate service runs comprehensive validation
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'