import click


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.group()
@click.pass_context
def shopify(ctx):
    "Commands related to Shopify."
    pass


@cli.group()
@click.pass_context
def git(ctx):
    "Commands related to Git."
    pass


# Load plugins dynamically
def load_plugins():
    try:
        # Try relative imports first (when installed as package)
        try:
            from .plugins.git import status, update
            from .plugins.shopify import theme, printess
        except ImportError:
            # Fall back to absolute imports (when run as script)
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from cli.plugins.git import status, update
            from cli.plugins.shopify import theme, printess

        shopify.add_command(theme)
        shopify.add_command(printess)
        git.add_command(status)
        git.add_command(update)
    except ImportError as e:
        click.echo(f"Error loading plugins: {e}")


def main():
    """Entry point for the CLI."""
    load_plugins()
    cli()


if __name__ == "__main__":
    main()
