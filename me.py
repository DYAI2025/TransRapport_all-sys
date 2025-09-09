#!/usr/bin/env python3
"""
TransRapport CLI Entry Point v0.1.0-pilot
Constitutional analysis following LD-3.4 framework
FROZEN RELEASE - Production ready
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.cli.main import main_cli

if __name__ == '__main__':
    main_cli()