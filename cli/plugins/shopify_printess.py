import os
from concurrent.futures import ThreadPoolExecutor
import click
import requests


@click.group()
@click.pass_context
def printess(ctx):
    """Commands for managing Shopify themes."""
    pass


@printess.command()
@click.pass_context
def update(ctx):
    """Update the Shopify theme."""

    files_to_update = {
        "snippets/printess-add-to-basket.liquid": "https://gist.githubusercontent.com/PrintessEditor/eaf528a693e44b4d7c1efde7fa50d8dd/raw/5b218b8278a536c2c39824fd76c80e5072dd1133/printess-add-to-basket.liquid",
        "snippets/printess-cart-edit-button.liquid": "https://gist.githubusercontent.com/PrintessEditor/eaf528a693e44b4d7c1efde7fa50d8dd/raw/5b218b8278a536c2c39824fd76c80e5072dd1133/printess-cart-edit-button.liquid",
        "snippets/printess-thumbnail.liquid": "https://gist.githubusercontent.com/PrintessEditor/eaf528a693e44b4d7c1efde7fa50d8dd/raw/5b218b8278a536c2c39824fd76c80e5072dd1133/printess-thumbnail.liquid",
        "assets/printesseditor.css": "https://gist.githubusercontent.com/PrintessEditor/eaf528a693e44b4d7c1efde7fa50d8dd/raw/5b218b8278a536c2c39824fd76c80e5072dd1133/printesseditor.css",
        "assets/printessShopify.js": "https://gist.githubusercontent.com/PrintessEditor/eaf528a693e44b4d7c1efde7fa50d8dd/raw/5b218b8278a536c2c39824fd76c80e5072dd1133/printessShopify.js",
        "assets/printessEditor.js": "https://gist.githubusercontent.com/PrintessEditor/eaf528a693e44b4d7c1efde7fa50d8dd/raw/5b218b8278a536c2c39824fd76c80e5072dd1133/printessEditor.js",
        "snippets/printess-render-design-now-button.liquid": "https://gist.githubusercontent.com/PrintessEditor/eaf528a693e44b4d7c1efde7fa50d8dd/raw/5b218b8278a536c2c39824fd76c80e5072dd1133/render-design-now%2520button.liquid",
        "snippets/printess-theme.liquid": "https://gist.githubusercontent.com/PrintessEditor/eaf528a693e44b4d7c1efde7fa50d8dd/raw/5b218b8278a536c2c39824fd76c80e5072dd1133/theme.liquid",
    }

    # Start downloading
    _download_files_in_parallel(files_to_update)
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
