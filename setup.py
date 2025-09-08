"""Setup script for TransRapport doc-validator."""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="transrapport-doc-validator",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "me=doc_validator.cli.main:main",
        ],
    },
    python_requires=">=3.11",
    author="TransRapport Team",
    description="Documentation validation and cross-reference management for TransRapport",
)