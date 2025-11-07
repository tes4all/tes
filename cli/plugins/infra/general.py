import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import click
import requests

try:
    from .. import utils
except ImportError:
    from cli.plugins import utils


@click.group()
@click.pass_context
def init(ctx):
    pass


@init.command()
@click.pass_context
def sshkeys(ctx):
    """Generate ssh keys if not exists."""


    ssh_dir = os.path.expanduser("~/.ssh")
    private_key_path = os.path.join(ssh_dir, "id_rsa")
    public_key_path = os.path.join(ssh_dir, "id_rsa.pub")

    if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
        os.makedirs(ssh_dir, exist_ok=True)
        utils.cmd_exec(
            [
                "ssh-keygen",
                "-t",
                "ed25519",
                "-f",
                private_key_path,
                "-N",
                "",
            ]
        )
        click.echo("SSH keys generated.")
    else:
        click.echo("SSH keys already exist. No action taken.")
