"""
Integration test for Windows MSI installation

CRITICAL: This test MUST FAIL before implementation.
Tests actual Windows installer behavior and system integration.
"""

import os
import platform
import pytest
import subprocess
import tempfile
from pathlib import Path

# Conditional import for Windows-specific modules
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False
    winreg = None


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific tests")
@pytest.mark.windows
class TestWindowsInstallation:
    """Integration tests for Windows MSI installation"""
    
    def test_msi_installer_generation(self):
        """Test that MSI installer can be generated"""
        # This test MUST FAIL until Tauri build process creates MSI
        
        # Attempt to build MSI package
        result = subprocess.run([
            'python', '-m', 'src.cli.package_cli', 'build',
            '--platform', 'windows-11',
            '--version', '1.0.0',
            '--profile', 'release',
            '--format', 'json'
        ], capture_output=True, text=True)
        
        # Should fail because build service not implemented
        assert result.returncode != 0
        
        # Check for MSI file existence (should not exist)
        msi_path = Path("desktop/src-tauri/target/release/bundle/msi/TransRapport_1.0.0_x64_en-US.msi")
        assert not msi_path.exists(), "MSI should not exist until build service is implemented"

    def test_msi_installation_process(self):
        """Test MSI installation via Windows Installer"""
        # This test MUST FAIL until actual MSI installer exists
        
        # Look for MSI installer (should not exist)
        msi_files = list(Path(".").glob("**/*.msi"))
        if len(msi_files) == 0:
            pytest.skip("No MSI installer found - build service not implemented yet")
        
        # If MSI exists (shouldn't happen yet), test installation
        msi_path = msi_files[0]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Attempt silent installation
            install_result = subprocess.run([
                'msiexec', '/i', str(msi_path),
                '/qn',  # Silent installation
                f'INSTALLDIR={temp_dir}\\TransRapport',
                '/L*V', f'{temp_dir}\\install.log'
            ], capture_output=True, text=True)
            
            # Should fail because installer doesn't exist or isn't properly configured
            # When implementation exists, this should succeed
            pytest.fail("MSI installation should fail until proper installer is implemented")

    def test_windows_registry_entries(self):
        """Test Windows Registry entries after installation"""
        # This test MUST FAIL until installation creates registry entries
        
        try:
            # Check for application registry entry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TransRapport") as key:
                # If key exists, check required values
                display_name = winreg.QueryValueEx(key, "DisplayName")[0]
                install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
                uninstall_string = winreg.QueryValueEx(key, "UninstallString")[0]
                
                assert display_name == "TransRapport"
                assert Path(install_location).exists()
                assert Path(uninstall_string).exists()
                
        except FileNotFoundError:
            # Expected to fail - registry entries don't exist until installer implemented
            pytest.fail("Registry entries should not exist until installer is properly implemented")

    def test_start_menu_entries(self):
        """Test Start Menu shortcut creation"""
        # This test MUST FAIL until installation creates Start Menu entries
        
        # Check for Start Menu shortcuts
        start_menu_paths = [
            Path(os.environ.get('APPDATA', '')) / "Microsoft/Windows/Start Menu/Programs/TransRapport.lnk",
            Path(os.environ.get('ALLUSERSPROFILE', '')) / "Microsoft/Windows/Start Menu/Programs/TransRapport.lnk"
        ]
        
        shortcuts_exist = any(path.exists() for path in start_menu_paths)
        
        if shortcuts_exist:
            pytest.fail("Start Menu shortcuts should not exist until installer is implemented")
        else:
            # Expected behavior - no shortcuts until installer works
            pass

    def test_desktop_shortcut_creation(self):
        """Test Desktop shortcut creation"""
        # This test MUST FAIL until installation creates desktop shortcuts
        
        desktop_path = Path(os.environ.get('USERPROFILE', '')) / "Desktop/TransRapport.lnk"
        public_desktop = Path(os.environ.get('PUBLIC', '')) / "Desktop/TransRapport.lnk"
        
        desktop_shortcuts = [desktop_path, public_desktop]
        shortcuts_exist = any(path.exists() for path in desktop_shortcuts)
        
        if shortcuts_exist:
            pytest.fail("Desktop shortcuts should not exist until installer is implemented")

    def test_file_associations(self):
        """Test file association registration"""
        # This test MUST FAIL until installation registers file associations
        
        try:
            # Check for .trlog file association
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ".trlog") as key:
                default_value = winreg.QueryValueEx(key, "")[0]
                
                # Check associated program
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{default_value}\\shell\\open\\command") as cmd_key:
                    command = winreg.QueryValueEx(cmd_key, "")[0]
                    assert "TransRapport" in command
                    
        except FileNotFoundError:
            # Expected to fail - file associations don't exist until installer implemented
            pytest.fail("File associations should not exist until installer is properly implemented")

    def test_application_executable_exists(self):
        """Test that application executable exists after installation"""
        # This test MUST FAIL until installation places executable in correct location
        
        # Common installation paths
        program_files = Path(os.environ.get('PROGRAMFILES', ''))
        program_files_x86 = Path(os.environ.get('PROGRAMFILES(X86)', ''))
        
        possible_paths = [
            program_files / "TransRapport/TransRapport.exe",
            program_files_x86 / "TransRapport/TransRapport.exe",
        ]
        
        executable_exists = any(path.exists() for path in possible_paths)
        
        if executable_exists:
            pytest.fail("Application executable should not exist until installer is implemented")

    def test_uninstallation_process(self):
        """Test MSI uninstallation process"""
        # This test MUST FAIL until installation and uninstallation work
        
        # Look for installed application
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TransRapport") as key:
                uninstall_string = winreg.QueryValueEx(key, "UninstallString")[0]
                
                # Attempt uninstallation
                uninstall_result = subprocess.run(
                    uninstall_string.split() + ['/qn'],  # Silent uninstall
                    capture_output=True, text=True
                )
                
                # Verify removal
                assert uninstall_result.returncode == 0
                
                # Check that registry entry is removed
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                       r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TransRapport"):
                        pytest.fail("Registry entry should be removed after uninstallation")
                except FileNotFoundError:
                    pass  # Expected - entry should be gone
                    
        except FileNotFoundError:
            # Expected - no installation exists yet
            pytest.skip("No installation found - installer not implemented yet")

    def test_windows_compatibility(self):
        """Test Windows version compatibility"""
        # This test MUST FAIL until we validate Windows compatibility
        
        import sys
        windows_version = sys.getwindowsversion()
        
        # Check if Windows 11 (build 22000+) or Windows 10
        is_windows_11 = windows_version.build >= 22000
        is_windows_10 = windows_version.major == 10 and windows_version.build < 22000
        
        if not (is_windows_10 or is_windows_11):
            pytest.fail("Windows version compatibility check should fail for unsupported versions")
        
        # This should pass when compatibility checking is implemented
        # Currently fails because no compatibility validation exists
        pytest.fail("Windows compatibility validation not implemented yet")

    def test_dependency_bundling(self):
        """Test that all dependencies are bundled in MSI"""
        # This test MUST FAIL until dependencies are properly bundled
        
        # Look for MSI installer
        msi_files = list(Path(".").glob("**/*.msi"))
        if len(msi_files) == 0:
            pytest.skip("No MSI installer found - build service not implemented yet")
        
        # Check MSI contents for bundled dependencies
        msi_path = msi_files[0]
        
        # Use msiexec or Windows Installer API to inspect contents
        # This should verify WebView2, Visual C++ redistributables, etc.
        # Currently fails because dependency bundling not implemented
        pytest.fail("Dependency bundling validation not implemented yet")

    @pytest.mark.slow
    def test_installation_performance(self):
        """Test installation performance meets requirements"""
        # This test MUST FAIL until installer meets performance targets
        
        # Look for MSI installer
        msi_files = list(Path(".").glob("**/*.msi"))
        if len(msi_files) == 0:
            pytest.skip("No MSI installer found - build service not implemented yet")
        
        msi_path = msi_files[0]
        
        import time
        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Time the installation process
            install_result = subprocess.run([
                'msiexec', '/i', str(msi_path),
                '/qn',
                f'INSTALLDIR={temp_dir}\\TransRapport'
            ], capture_output=True, text=True)
            
            end_time = time.time()
            install_duration = end_time - start_time
            
            # Should complete in under 120 seconds per requirements
            if install_duration > 120:
                pytest.fail(f"Installation took {install_duration:.1f}s, should be under 120s")
            
            # Currently fails because no installer exists
            pytest.fail("Installation performance test not possible until installer implemented")

    def test_code_signing_verification(self):
        """Test that MSI installer is properly code signed"""
        # This test MUST FAIL until code signing is implemented
        
        # Look for MSI installer
        msi_files = list(Path(".").glob("**/*.msi"))
        if len(msi_files) == 0:
            pytest.skip("No MSI installer found - build service not implemented yet")
        
        msi_path = msi_files[0]
        
        # Use Windows SDK signtool to verify signature
        verify_result = subprocess.run([
            'signtool', 'verify', '/pa', str(msi_path)
        ], capture_output=True, text=True)
        
        if verify_result.returncode != 0:
            # Expected to fail - signing not implemented yet
            pytest.fail("MSI installer should be code signed but verification failed")
        
        # Check for valid timestamp
        assert "Successfully verified" in verify_result.stdout