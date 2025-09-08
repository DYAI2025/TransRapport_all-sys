"""Main CLI entry point for TransRapport documentation validation."""
import click


@click.group()
@click.version_option("1.0.0")
def main():
    """TransRapport marker engine CLI."""
    pass


@main.group()
def docs():
    """Documentation validation and cross-reference management."""
    pass


if __name__ == "__main__":
    main()