import importlib
import os
import pkgutil
import sys
from typing import Iterable

import click


PLUGIN_PACKAGE = "cli.plugins"


@click.group()
@click.pass_context
def cli(ctx):
    """TES command line interface."""
    pass


def _ensure_plugins_package():
    """Import the plugins package, adjusting sys.path when needed."""
    try:
        return importlib.import_module(PLUGIN_PACKAGE)
    except ImportError:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
        return importlib.import_module(PLUGIN_PACKAGE)


def _collect_commands(module) -> Iterable[click.core.Command]:
    exported_names = getattr(module, "__all__", None)
    if exported_names is None:
        exported_names = [name for name in dir(module) if not name.startswith("_")]

    for name in exported_names:
        command = getattr(module, name, None)
        if isinstance(command, click.core.Command):
            yield command


def load_plugins(root_cli: click.Group) -> None:
    """Discover plugin packages and register their commands dynamically."""
    plugins_pkg = _ensure_plugins_package()

    for _, plugin_name, is_pkg in pkgutil.iter_modules(plugins_pkg.__path__):
        if not is_pkg or plugin_name.startswith("_"):
            continue

        module_name = f"{PLUGIN_PACKAGE}.{plugin_name}"

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            click.echo(f"Error importing plugin '{plugin_name}': {exc}")
            continue

        if hasattr(module, "register"):
            try:
                module.register(root_cli)
            except Exception as exc:
                click.echo(f"Error registering plugin '{plugin_name}': {exc}")
            continue

        existing = getattr(module, plugin_name, None)
        if isinstance(existing, click.core.Command):
            if existing.name in root_cli.commands:
                continue
            root_cli.add_command(existing)
            continue

        commands = list(_collect_commands(module))
        if not commands:
            continue

        help_text = (module.__doc__ or "").strip().splitlines()
        group_help = help_text[0] if help_text else None
        plugin_group = click.Group(name=plugin_name, help=group_help)

        for command in commands:
            plugin_group.add_command(command)

        if plugin_group.name in root_cli.commands:
            continue
        root_cli.add_command(plugin_group)


def main():
    """Entry point for the CLI."""
    load_plugins(cli)
    cli()


if __name__ == "__main__":
    main()
