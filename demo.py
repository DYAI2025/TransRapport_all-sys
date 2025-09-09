#!/usr/bin/env python3
"""
TransRapport End-to-End Demo Script
Demonstrates complete constitutional analysis workflow
"""

import subprocess
import sys
import os
from pathlib import Path

# Demo configuration
DEMO_PASSPHRASE = "demo123"
DEMO_CONV = "demo"
DEMO_TEXT = "samples/demo.txt"

def run_cli_command(command, input_text=None):
    """Run CLI command and return output"""
    try:
        # Add current directory to Python path
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd() / 'src')
        
        process = subprocess.Popen(
            ['python3', 'me.py'] + command.split()[1:],  # Skip 'me' prefix
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            env=env
        )
        
        stdout, stderr = process.communicate(input=input_text)
        
        print(f"$ me {command}")
        if stdout:
            print(stdout)
        if stderr and process.returncode != 0:
            print(f"Error: {stderr}", file=sys.stderr)
        
        return process.returncode == 0, stdout, stderr
        
    except Exception as e:
        print(f"Failed to run command: {e}")
        return False, "", str(e)

def main():
    """Run the complete end-to-end demo"""
    print("🚀 TransRapport End-to-End Demo")
    print("=" * 50)
    print("Demonstrating LD-3.4 constitutional analysis workflow")
    print()
    
    # Step 1: Initialize database
    print("📋 Step 1: Initialize TransRapport")
    print("-" * 30)
    success, stdout, stderr = run_cli_command("init", f"{DEMO_PASSPHRASE}\n{DEMO_PASSPHRASE}\n")
    if not success:
        print("❌ Initialization failed")
        return
    print("✅ TransRapport initialized")
    print()
    
    # Step 2: Load constitutional markers
    print("📋 Step 2: Load Constitutional Markers")
    print("-" * 40)
    success, stdout, stderr = run_cli_command("markers load")
    if not success:
        print("❌ Marker loading failed")
        return
    print("✅ Constitutional markers loaded")
    print()
    
    # Step 3: Validate constitutional compliance
    print("📋 Step 3: Validate Constitutional Compliance")
    print("-" * 45)
    success, stdout, stderr = run_cli_command("markers validate --strict")
    if not success:
        print("❌ Marker validation failed")
        return
    print("✅ Constitutional compliance verified")
    print()
    
    # Step 4: Create analysis job
    print("📋 Step 4: Create Analysis Job")
    print("-" * 30)
    success, stdout, stderr = run_cli_command(
        f"job create --conv {DEMO_CONV} --text {DEMO_TEXT}",
        f"{DEMO_PASSPHRASE}\n"
    )
    if not success:
        print("❌ Job creation failed")
        return
    print("✅ Analysis job created")
    print()
    
    # Step 5: Execute constitutional analysis scan
    print("📋 Step 5: Execute Constitutional Analysis")
    print("-" * 40)
    success, stdout, stderr = run_cli_command(
        f"run scan --conv {DEMO_CONV}",
        f"{DEMO_PASSPHRASE}\n"
    )
    if not success:
        print("❌ Analysis scan failed")
        return
    print("✅ LD-3.4 constitutional analysis completed")
    print()
    
    # Step 6: View semantic markers
    print("📋 Step 6: View Semantic Markers")
    print("-" * 30)
    success, stdout, stderr = run_cli_command(
        f"view events --conv {DEMO_CONV} --level sem --last 20",
        f"{DEMO_PASSPHRASE}\n"
    )
    if not success:
        print("❌ Event viewing failed")
        return
    print("✅ Semantic markers displayed")
    print()
    
    # Step 7: Export all events
    print("📋 Step 7: Export All Constitutional Events")
    print("-" * 42)
    success, stdout, stderr = run_cli_command(
        f"export events --conv {DEMO_CONV} --level all --out exports/{DEMO_CONV}/",
        f"{DEMO_PASSPHRASE}\n"
    )
    if not success:
        print("❌ Event export failed")
        return
    print("✅ Constitutional events exported")
    print()
    
    print("🎉 END-TO-END DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("🏛️  Constitutional Framework: LD-3.4")
    print("📊 Analysis Method: Constitutional marker detection")
    print("🔐 Storage: SQLCipher encrypted database")
    print("📤 Export: Multiple formats with compliance statements")
    print()
    print("📁 Check the exports/demo/ directory for generated reports")
    print("✅ All operations maintained constitutional compliance")

if __name__ == '__main__':
    main()