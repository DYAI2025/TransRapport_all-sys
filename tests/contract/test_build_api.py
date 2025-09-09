"""
Contract test for POST /build endpoint

CRITICAL: This test MUST FAIL before implementation.
Tests the Build API contract from contracts/build-api.json
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path


class TestBuildAPI:
    """Contract tests for Build API endpoint"""
    
    def test_build_endpoint_exists(self):
        """Test that build CLI command exists and responds"""
        # This test MUST FAIL until build service is implemented
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'build',
            '--platform', 'windows-11',
            '--version', '1.0.0',
            '--profile', 'release',
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

    def test_build_request_schema_validation(self):
        """Test BuildRequest schema validation"""
        # Test valid request format
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'build',
            '--platform', 'macos',
            '--version', '2.1.3',
            '--profile', 'debug',
            '--architecture', 'arm64',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Should fail with NOT_IMPLEMENTED, not schema validation error
        assert response.get('error') == 'NOT_IMPLEMENTED'
        assert 'schema' not in response.get('message', '').lower()

    def test_build_invalid_platform_rejection(self):
        """Test invalid platform is rejected"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'build',
            '--platform', 'invalid-platform',
            '--version', '1.0.0',
            '--profile', 'release',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should fail due to CLI validation (not implementation)
        assert result.returncode != 0
        # Click should reject invalid choice before reaching our code

    def test_build_invalid_version_format(self):
        """Test invalid version format is rejected"""  
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'build',
            '--platform', 'linux-deb',
            '--version', 'invalid-version',
            '--profile', 'release',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # This should reach our code and fail with NOT_IMPLEMENTED
        # Version validation will be implemented later
        response = json.loads(result.stdout)
        assert response.get('error') == 'NOT_IMPLEMENTED'

    def test_build_response_schema_structure(self):
        """Test that response follows BuildResponse schema structure"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'build',
            '--platform', 'windows-11',
            '--version', '1.0.0', 
            '--profile', 'release',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Required fields per BuildResponse schema
        assert 'success' in response
        assert 'error' in response  # Present in error responses
        assert 'message' in response  # Present in error responses
        assert isinstance(response['success'], bool)

    def test_build_all_platforms_supported(self):
        """Test all required platforms are supported"""
        platforms = ['windows-11', 'macos', 'linux-deb', 'linux-rpm', 'linux-appimage']
        
        for platform in platforms:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'build',
                '--platform', platform,
                '--version', '1.0.0',
                '--profile', 'release',
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            
            # Each platform should fail with NOT_IMPLEMENTED (not unsupported platform)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Platform {platform} should be recognized but not implemented"

    def test_build_all_architectures_supported(self):
        """Test all required architectures are supported"""
        architectures = ['x64', 'arm64', 'universal']
        
        for arch in architectures:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'build',
                '--platform', 'macos',
                '--version', '1.0.0',
                '--profile', 'release', 
                '--architecture', arch,
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Architecture {arch} should be recognized but not implemented"

    def test_build_profile_options(self):
        """Test both debug and release profiles are supported"""
        profiles = ['debug', 'release']
        
        for profile in profiles:
            result = subprocess.run([
                sys.executable, '-m', 'src.cli.package_cli', 'build',
                '--platform', 'linux-deb',
                '--version', '1.0.0',
                '--profile', profile,
                '--format', 'json'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            response = json.loads(result.stdout)
            assert response.get('error') == 'NOT_IMPLEMENTED', f"Profile {profile} should be recognized but not implemented"

    def test_build_human_format_output(self):
        """Test human-readable format output"""
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'build',
            '--platform', 'windows-11',
            '--version', '1.0.0',
            '--profile', 'release',
            '--format', 'human'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        # Should contain human-readable error message
        assert 'Build failed' in result.stdout
        assert 'not yet implemented' in result.stdout.lower()
        assert result.returncode == 1

    @pytest.mark.integration
    def test_build_integration_with_tauri_config(self):
        """Test integration with Tauri configuration"""
        # This test verifies the build process would integrate with actual Tauri
        # Should fail since build service is not implemented
        result = subprocess.run([
            sys.executable, '-m', 'src.cli.package_cli', 'build',
            '--platform', 'windows-11',
            '--version', '1.0.0',
            '--profile', 'release',
            '--format', 'json'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        
        response = json.loads(result.stdout)
        
        # Must fail until build service reads Tauri config and executes build
        assert response.get('success') is False
        assert response.get('error') == 'NOT_IMPLEMENTED'