import os
import json
import yaml
import click


def register(cli_group):
    @cli_group.group()
    def shopify():
        """Commands for Shopify management."""
        pass

    @shopify.group()
    def theme():
        """Commands for managing Shopify themes."""
        pass

    @shopify.command("init")
    @click.option("--shop-name")
    def initrepo(shop_name):
        # create git branches
        for branch in BRANCHES:
            os.system(f"git checkout -b {branch}")
            # push to remote
            os.system(f"git push -u origin {branch}")

    def update_theme(shop_name, theme_name, theme_version):
        pass


def _get_theme_info():
    # read file config/settings_schema.json
    # get current folder
    with open(os.path.join(BASE_FOLDER, "./config/settings_schema.json")) as f:
        settings_schema = json.load(f)
    # get by name "theme_info"
    for setting in settings_schema:
        if setting["name"] == "theme_info":
            return setting
    raise Exception("Theme info not found in settings schema")


def _get_config():
    # read .tes.yml file
    with open(os.path.join(BASE_FOLDER, ".tes.yml")) as f:
        return yaml.safe_load(f)
