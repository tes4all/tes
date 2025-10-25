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
        from cli.plugins import (
            shopify_theme,
            shopify_printess,
            git_tools,
        )  # Importing plugin modules

        shopify.add_command(shopify_theme.theme)
        shopify.add_command(shopify_printess.printess)
        git.add_command(git_tools.tools)
    except ImportError as e:
        click.echo(f"Error loading plugins: {e}")


def main():
    """Entry point for the CLI."""
    load_plugins()
    cli()


if __name__ == "__main__":
    main()
