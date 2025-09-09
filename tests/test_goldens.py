#!/usr/bin/env python3
"""
TransRapport v0.1.0-pilot Golden Tests
Snapshot tests to ensure CLI output consistency across releases
"""

import json
import subprocess
import tempfile
import os
from pathlib import Path

# Load expected outputs
GOLDENS_DIR = Path(__file__).parent / "goldens"
with open(GOLDENS_DIR / "cli_output_expected.json") as f:
    EXPECTED = json.load(f)


def run_cli_command(args):
    """Run CLI command and return result"""
    cmd = ["python3", "me.py"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": 124,  # timeout exit code
            "stdout": "",
            "stderr": "Command timed out"
        }


def test_version_compliance():
    """Test version and framework compliance"""
    result = run_cli_command(["status"])
    
    assert result["exit_code"] == EXPECTED["expected_commands"]["status"]["exit_code"]
    
    for required_text in EXPECTED["expected_commands"]["status"]["contains"]:
        assert required_text in result["stdout"], f"Missing required text: {required_text}"
    
    print("✅ Version compliance test passed")


def test_audio_devices_format():
    """Test audio devices output format"""
    result = run_cli_command(["audio", "devices"])
    
    assert result["exit_code"] == EXPECTED["expected_commands"]["audio_devices"]["exit_code"]
    
    # Test JSON format
    try:
        data = json.loads(result["stdout"])
        
        # Check required fields
        for field in EXPECTED["expected_commands"]["audio_devices"]["required_fields"]:
            assert field in data, f"Missing required field: {field}"
        
        # Check device fields if devices exist
        if data.get("devices") and len(data["devices"]) > 0:
            device = data["devices"][0]
            for field in EXPECTED["expected_commands"]["audio_devices"]["device_fields"]:
                assert field in device, f"Missing device field: {field}"
                
    except json.JSONDecodeError as e:
        assert False, f"Invalid JSON output: {e}"
    
    print("✅ Audio devices format test passed")


def test_transcription_format():
    """Test transcription output format"""
    # Create test session
    test_session = f"test-golden-{os.getpid()}"
    
    # Create session directory and test file
    session_dir = Path(f"sessions/{test_session}")
    session_dir.mkdir(parents=True, exist_ok=True)
    test_audio = session_dir / "raw.wav"
    test_audio.write_text("")  # Empty file for mock test
    
    try:
        result = run_cli_command(["transcribe", "transcribe", "--conv", test_session, "--output-json"])
        
        assert result["exit_code"] == EXPECTED["expected_commands"]["transcribe_mock"]["exit_code"]
        
        # Test JSON format
        data = json.loads(result["stdout"])
        
        # Check required fields
        for field in EXPECTED["expected_commands"]["transcribe_mock"]["required_fields"]:
            assert field in data, f"Missing required field: {field}"
        
        # Check segment fields if segments exist
        if data.get("segments") and len(data["segments"]) > 0:
            segment = data["segments"][0]
            for field in EXPECTED["expected_commands"]["transcribe_mock"]["segment_fields"]:
                assert field in segment, f"Missing segment field: {field}"
        
        print("✅ Transcription format test passed")
        
    finally:
        # Cleanup
        import shutil
        if session_dir.exists():
            shutil.rmtree(session_dir)


def test_diarization_format():
    """Test diarization output format"""
    test_session = f"test-golden-diar-{os.getpid()}"
    
    # Create session directory and test file
    session_dir = Path(f"sessions/{test_session}")
    session_dir.mkdir(parents=True, exist_ok=True)
    test_audio = session_dir / "raw.wav"
    test_audio.write_text("")  # Empty file for mock test
    
    try:
        result = run_cli_command(["diarize", "diarize", "--conv", test_session, "--output-json"])
        
        assert result["exit_code"] == EXPECTED["expected_commands"]["diarize_mock"]["exit_code"]
        
        # Test JSON format
        data = json.loads(result["stdout"])
        
        # Check required fields
        for field in EXPECTED["expected_commands"]["diarize_mock"]["required_fields"]:
            assert field in data, f"Missing required field: {field}"
            
        print("✅ Diarization format test passed")
        
    finally:
        # Cleanup
        import shutil
        if session_dir.exists():
            shutil.rmtree(session_dir)


def test_frozen_markers_compliance():
    """Test that markers match frozen v0.1.0 specification"""
    # This test would check loaded markers against frozen spec
    # For now, validate the frozen config can be loaded
    
    from src.config.v0_1_0_defaults import get_v010_config, FROZEN_MARKERS_V0_1_0
    
    config = get_v010_config()
    markers = config.get_markers()
    
    # Verify all expected markers are present
    for marker_type in EXPECTED["frozen_markers"].keys():
        assert marker_type in markers, f"Missing frozen marker: {marker_type}"
        assert markers[marker_type]["enabled"] == EXPECTED["frozen_markers"][marker_type]["enabled"]
    
    # Verify frozen defaults
    assert config.confidence_threshold == EXPECTED["frozen_defaults"]["confidence_threshold"]
    assert config.default_window_sem == EXPECTED["frozen_defaults"]["default_window_sem"]
    assert config.default_window_clu == EXPECTED["frozen_defaults"]["default_window_clu"]
    
    print("✅ Frozen markers compliance test passed")


def test_desktop_ui_integration():
    """Test desktop UI can load and integrate with CLI"""
    # Check that bundled UI files exist
    ui_dist = Path("desktop/dist")
    assert ui_dist.exists(), "Desktop UI dist directory missing"
    
    index_html = ui_dist / "index.html"
    assert index_html.exists(), "Desktop UI index.html missing"
    
    # Check assets are bundled with relative paths
    content = index_html.read_text()
    assert "./assets/" in content, "UI assets not bundled with relative paths"
    assert "localhost" not in content, "UI contains localhost references"
    
    print("✅ Desktop UI integration test passed")


if __name__ == "__main__":
    print("🧪 Running TransRapport v0.1.0-pilot Golden Tests")
    print("=" * 50)
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    try:
        test_version_compliance()
        test_audio_devices_format()
        test_transcription_format()
        test_diarization_format()
        test_frozen_markers_compliance()
        test_desktop_ui_integration()
        
        print("\n🎉 All Golden Tests Passed!")
        print("v0.1.0-pilot release is compliant with specifications")
        
    except AssertionError as e:
        print(f"\n❌ Golden Test Failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n💥 Golden Test Error: {e}")
        exit(1)