import os
import json
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
import click
import requests

try:
    from .. import utils
except ImportError:
    from cli.plugins import utils


APP_NAME = "jep-projectvault"
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
    instructions = _load_json_file(instructions_path)

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
            # inject snippet immediately after the opening <body> tag or replace existing markers
            with open(source, "r") as sf:
                source_content = sf.read().rstrip()
            with open(destination, "r") as df:
                dest_content = df.read()

            start_marker = "{% comment %}$TES-" + APP_NAME + "-start${% endcomment %}"
            end_marker = "{% comment %}$TES-" + APP_NAME + "-end${% endcomment %}"
            snippet_block = f"{start_marker}\n{source_content}\n{end_marker}"

            if start_marker in dest_content and end_marker in dest_content:
                # replace the existing block to avoid duplicate insertions
                pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
                new_content = pattern.sub(snippet_block, dest_content, count=1)
            else:
                body_match = re.search(r"<body[^>]*>", dest_content, flags=re.IGNORECASE)
                if not body_match:
                    raise click.ClickException("theme.liquid is missing a <body> tag to inject the Project Vault snippet.")
                insertion_point = body_match.end()
                new_content = dest_content[:insertion_point] + "\n" + snippet_block + dest_content[insertion_point:]

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

    integration_config = _load_json_file(integration_config_file)
    shopify_settings_schema = _load_json_file(shopify_settings_schema_path)

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


def _load_json_file(file_path):
    """Load JSON while tolerating trailing commas in arrays/objects."""
    with open(file_path, "r") as handle:
        raw_content = handle.read()
    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as exc:
        sanitized = _strip_trailing_commas(raw_content)
        if sanitized != raw_content:
            try:
                return json.loads(sanitized)
            except json.JSONDecodeError as sanitized_exc:
                raise click.ClickException(f"Invalid JSON in {file_path}: {sanitized_exc}") from sanitized_exc
        raise click.ClickException(f"Invalid JSON in {file_path}: {exc}") from exc


def _strip_trailing_commas(payload):
    """Remove trailing commas before closing braces/brackets outside strings."""
    result = []
    in_string = False
    escape = False

    for char in payload:
        if in_string:
            result.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            result.append(char)
            continue

        if char in (']', '}'):
            idx = len(result) - 1
            # walk back over whitespace to find a potential trailing comma
            while idx >= 0 and result[idx].isspace():
                idx -= 1
            if idx >= 0 and result[idx] == ',':
                # drop the comma and any whitespace after it that we already added
                while len(result) - 1 >= idx:
                    result.pop()
        result.append(char)

    return ''.join(result)

