import os
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
import click
import requests

try:
    from .. import utils
except ImportError:
    from cli.plugins import utils


APP_NAME = "jep-project-vault"
TEMP_DIR = "project_vault_temp"
INTEGRATION_BASE_PATH = os.path.join("integrations", "printess", "shopify")

@click.group()
@click.pass_context
def project_vault(ctx):
    """Commands for managing Shopify themes."""
    pass


@project_vault.command()
@click.pass_context
def update(ctx):
    """Update the Shopify theme."""

    printess_gist_url = "git@github.com:jep-hq/ProjectVault.git"
    # rm dir if exists
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    # clone gist
    utils.cmd_exec(["git", "clone", printess_gist_url, TEMP_DIR])

    # read instructions.json in integrations/printess/shopify
    """
{
  "requirements": [
    "alpine",
    "tailwindcss"
  ],
  "files": [
    {
      "name": "jep-projectvault-printess-global-config.liquid",
      "folder": "snippets",
      "action": "replace"
    },
    {
      "name": "jep-projectvault.liquid",
      "folder": "snippets",
      "action": "replace"
    },
    {
      "name": "theme.liquid",
      "folder": "layout",
      "action": "after_body_open"
    }
  ]
}

"""
    instructions_path = os.path.join(TEMP_DIR, INTEGRATION_BASE_PATH, "instructions.json")
    with open(instructions_path, "r") as f:
        instructions = json.load(f)

    # handle files
    files_to_download = instructions.get("files", {})
    for file in files_to_download:
        file_name = file["name"]
        folder = file["folder"]
        source = os.path.join(TEMP_DIR, INTEGRATION_BASE_PATH, file_name)
        destination = os.path.join(utils.WORK_FOLDER, folder, file_name)
        # check action
        if file["action"] == "replace":
            shutil.move(source, destination)
        elif file["action"] == "after_body_open":
            # read source content
            with open(source, "r") as sf:
                source_content = sf.read()
            # read destination content
            with open(destination, "r") as df:
                dest_content = df.read()
            # replace content from {% comment %}$TES-jep-project-vault-start${% endcomment %} to {% comment %}$TES-jep-project-vault-end${% endcomment %} in dest_content
            start_marker = "{% comment %}$TES-" + APP_NAME + "-start${% endcomment %}"
            end_marker = "{% comment %}$TES-" + APP_NAME + "-end${% endcomment %}"

            if start_marker in dest_content and end_marker in dest_content:
                start_idx = dest_content.find(start_marker)
                end_idx = dest_content.find(end_marker) + len(end_marker)
                new_content = dest_content[:start_idx] + "" + dest_content[end_idx:]

            new_content = dest_content.replace("<body>", "<body>\n" + start_marker + "\n" + source_content + "\n" + end_marker)
            # write back to destination
            with open(destination, "w") as df:
                df.write(new_content)

    # settings
    _set_schema_in_settings()

    # remove temp folder
    shutil.rmtree(TEMP_DIR)
    click.echo("Shopify jep projectvault updated!")


def _set_schema_in_settings():
    """Set or update a schema in the settings_schema list."""
    # load settings_schema.json
    integration_config_file = os.path.join(TEMP_DIR, INTEGRATION_BASE_PATH, "shopify_config.json")
    if not os.path.exists(integration_config_file):
        return True

    shopify_settings_schema_path = os.path.join(utils.WORK_FOLDER, "config", "settings_schema.json")
    if not os.path.exists(shopify_settings_schema_path):
        return True

    with open(integration_config_file, "r") as scf:
        integration_config = json.load(scf)
    with open(shopify_settings_schema_path, "r") as scf:
        shopify_settings_schema = json.load(scf)

    has_changes = False
    for schema_name in integration_config.get("settings", {}).get("schema", []):
        schema_settings = integration_config["settings"]["schema"][schema_name]

        found = False
        # find schemna by name in shopify_settings_schema and replace it
        for shopify_schema in shopify_settings_schema:
            if shopify_schema.get("name") == schema_name:
                # replace schema
                shopify_schema["settings"] = schema_settings
                found = True
                break
        if not found:
            # append schema
            shopify_settings_schema.append({
                "name": schema_name,
                "settings": schema_settings
            })


    # write back to settings_schema.json
    with open(shopify_settings_schema_path, "w") as ssf:
        json.dump(shopify_settings_schema, ssf, indent=2)
    return True

