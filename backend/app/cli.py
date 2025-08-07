"""CLI tools for administration."""

import click

from backend.app.auth.api_key import generate_api_key


@click.group()
def cli():
    """Football Lineup Bot administration tools."""
    pass


@cli.command()
def generate_key():
    """Generate a secure API key."""
    api_key = generate_api_key()
    click.echo(f"Generated API key: {api_key}")
    click.echo("Add this to your .env file as API_KEY=<key>")


if __name__ == "__main__":
    cli()
