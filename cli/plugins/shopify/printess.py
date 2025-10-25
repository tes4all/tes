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
def printess(ctx):
    """Commands for managing Shopify themes."""
    pass


@printess.command()
@click.pass_context
def update(ctx):
    """Update the Shopify theme."""

    printess_gist_url = "git@github.com:PrintessEditor/Printess-Shopify-Plugin.git"
    # rm dir if exists
    if os.path.exists("printess_temp"):
        shutil.rmtree("printess_temp")

    # clone gist
    utils.cmd_exec(["git", "clone", printess_gist_url, "printess_temp"])

    files_to_move = {
        "printess-add-to-basket.liquid": "snippets/printess-add-to-basket.liquid",
        "printess-cart-edit-button.liquid": "snippets/printess-cart-edit-button.liquid",
        "printess-thumbnail.liquid": "snippets/printess-thumbnail.liquid",
        "printesseditor.css": "assets/printesseditor.css",
        "printessShopify.js": "assets/printessShopify.js",
        "printessEditor.js": "assets/printessEditor.js",
        "render-design-now button.liquid": "snippets/printess-render-design-now-button.liquid",
        "theme.liquid": "snippets/printess-theme.liquid",
    }

    # Start downloading
    for file_name, destination in files_to_move.items():
        source = os.path.join("printess_temp", file_name)
        destination = os.path.join(utils.WORK_FOLDER, destination)
        shutil.move(source, destination)

    # remove temp folder
    shutil.rmtree("printess_temp")
    click.echo("Shopify printess updated!")


def _download_file(file_path, url):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded: {file_path}")
    else:
        print(f"Failed to download {file_path}: {response.status_code}")


# Parallel download using ThreadPoolExecutor
def _download_files_in_parallel(files):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(_download_file, file_path, url)
            for file_path, url in files.items()
        ]
        for future in futures:
            future.result()
