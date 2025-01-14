import os
import click


@click.group()
@click.pass_context
def printess(ctx):
    """Commands for managing Shopify themes."""
    pass


@printess.command()
@click.pass_context
def update(ctx):
    """Update the Shopify theme."""
    click.echo("Shopify theme updated!")
