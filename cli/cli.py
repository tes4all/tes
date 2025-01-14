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


# Load plugins dynamically
def load_plugins():
    try:
        from plugins import shopify_theme, shopify_printess  # Importing plugin modules

        shopify.add_command(shopify_theme.theme)
        shopify.add_command(shopify_printess.printess)
    except ImportError as e:
        click.echo(f"Error loading plugins: {e}")


# cli = TES_CLI()

if __name__ == "__main__":
    load_plugins()
    cli()
