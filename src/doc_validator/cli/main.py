"""Main CLI entry point for TransRapport documentation validation."""
import click

from .validate_command import validate
from .crossref_command import cross_ref
from .status_command import status


@click.group()
@click.version_option("1.0.0")
def main():
    """TransRapport marker engine CLI."""
    pass


@main.group()
def docs():
    """Documentation validation and cross-reference management."""
    pass


# Add commands to docs group
docs.add_command(validate)
docs.add_command(cross_ref)
docs.add_command(status)


if __name__ == "__main__":
    main()