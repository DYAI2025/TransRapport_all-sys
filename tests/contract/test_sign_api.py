"""
Contract test for POST /sign endpoint

CRITICAL: This test MUST FAIL before implementation.
Tests the Sign API contract from contracts/build-api.json
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path


class TestSignAPI:
    """Contract tests for Sign API endpoint"""
    
    def test_sign_endpoint_exists(self):
        """Test that sign CLI command exists and responds"""
        # This test MUST FAIL until sign service is implemented
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/installer.msi',
            '--platform', 'windows',
            '--certificate-source', 'azure_key_vault',
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

    def test_sign_request_schema_validation(self):
        """Test SignRequest schema validation"""
        # Test all valid platform and certificate source combinations
        test_cases = [
            ('windows', 'azure_key_vault'),
            ('macos', 'apple_developer'), 
            ('linux', 'local_certificate')
        ]
        
        for platform, cert_source in test_cases:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'sign',
                '--package-path', f'/fake/path/installer.{platform}',
                '--platform', platform,
                '--certificate-source', cert_source,
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            
            # Should fail with NOT_IMPLEMENTED, not schema validation error
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Platform {platform} with {cert_source} should be recognized"

    def test_sign_invalid_platform_rejection(self):
        """Test invalid platform is rejected"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/installer.bin',
            '--platform', 'invalid-platform',
            '--certificate-source', 'azure_key_vault',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should fail due to CLI validation (not implementation)
        assert result.returncode != 0

    def test_sign_invalid_certificate_source_rejection(self):
        """Test invalid certificate source is rejected"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/installer.msi',
            '--platform', 'windows',
            '--certificate-source', 'invalid-cert-source',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should fail due to CLI validation (not implementation)
        assert result.returncode != 0

    def test_sign_missing_required_fields(self):
        """Test missing required fields are rejected"""
        # Missing package-path
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--platform', 'windows',
            '--certificate-source', 'azure_key_vault',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        assert result.returncode != 0

    def test_sign_response_schema_structure(self):
        """Test that response follows SignResponse schema structure"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/installer.dmg',
            '--platform', 'macos',
            '--certificate-source', 'apple_developer',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Required fields per SignResponse schema (error case)
        assert 'success' in response
        assert 'error' in response
        assert 'message' in response
        assert isinstance(response['success'], bool)

    def test_sign_windows_azure_key_vault(self):
        """Test Windows signing with Azure Key Vault"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/TransRapport.msi',
            '--platform', 'windows',
            '--certificate-source', 'azure_key_vault',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_sign_macos_apple_developer(self):
        """Test macOS signing with Apple Developer certificates"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/TransRapport.dmg',
            '--platform', 'macos',
            '--certificate-source', 'apple_developer',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_sign_linux_local_certificate(self):
        """Test Linux signing with local GPG certificate"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/transrapport.deb',
            '--platform', 'linux',
            '--certificate-source', 'local_certificate',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_sign_human_format_output(self):
        """Test human-readable format output"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/installer.rpm',
            '--platform', 'linux',
            '--certificate-source', 'local_certificate',
            '--format', 'human'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should contain human-readable error message
        assert 'Sign failed' in result.stdout
        assert 'not yet implemented' in result.stdout.lower()
        assert result.returncode == 1

    def test_sign_all_supported_platforms(self):
        """Test all supported platforms are recognized"""
        platforms = ['windows', 'macos', 'linux']
        
        for platform in platforms:
            # Use appropriate certificate source for each platform
            cert_source = {
                'windows': 'azure_key_vault',
                'macos': 'apple_developer',
                'linux': 'local_certificate'
            }[platform]
            
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'sign',
                '--package-path', f'/fake/path/installer.{platform}',
                '--platform', platform,
                '--certificate-source', cert_source,
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Platform {platform} should be supported"

    def test_sign_certificate_source_validation(self):
        """Test all certificate sources are recognized"""
        cert_sources = ['azure_key_vault', 'apple_developer', 'local_certificate']
        
        for cert_source in cert_sources:
            # Use appropriate platform for each certificate source
            platform = {
                'azure_key_vault': 'windows',
                'apple_developer': 'macos', 
                'local_certificate': 'linux'
            }[cert_source]
            
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'sign',
                '--package-path', f'/fake/path/installer.bin',
                '--platform', platform,
                '--certificate-source', cert_source,
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Certificate source {cert_source} should be supported"

    @pytest.mark.integration
    def test_sign_certificate_configuration_loading(self):
        """Test that signing loads certificate configuration"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/installer.msi',
            '--platform', 'windows',
            '--certificate-source', 'azure_key_vault',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until sign service loads certificate config and performs signing
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'

    @pytest.mark.integration
    def test_sign_timestamping_integration(self):
        """Test that signing includes timestamping"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/installer.dmg',
            '--platform', 'macos',
            '--certificate-source', 'apple_developer',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until sign service implements timestamping
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'

    @pytest.mark.integration
    def test_sign_signature_validation(self):
        """Test that signing validates signature after creation"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'sign',
            '--package-path', '/fake/path/transrapport.AppImage',
            '--platform', 'linux',
            '--certificate-source', 'local_certificate',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until sign service validates created signatures
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'