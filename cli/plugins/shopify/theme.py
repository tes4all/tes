import os
import shutil
import subprocess
import json
import click

try:
    from .. import utils
except ImportError:
    from cli.plugins import utils


@click.group()
@click.pass_context
def theme(ctx):
    """Commands for managing Shopify themes."""
    pass


@theme.command()
@click.pass_context
@click.option("--store", required=True)
def init(ctx, store):
    """Initialize the tes config and create the theme branches."""
    click.echo("Initializing...")
    click.echo(f"Store: {store}")
    click.echo(f"Working directory: {utils.WORK_FOLDER}")
    click.echo("Pull updates...")
    utils.cmd_exec(["git", "pull"])

    config = utils.get_config()
    if (
        not config.get("shopify")
        or not config["shopify"].get("store")
        or config["shopify"]["store"] != store
    ):
        _set_tes_config(config, store)

    theme_info = _get_theme_info()
    if not theme_info:
        click.echo("No theme info found.")
        click.echo("\rDownload latest raw theme from shopify...", nl=False)

        # get "DO_NOT_CHANGE_<theme_name>"
        theme_name = _get_theme_name(store)
        if not theme_name:
            click.echo("Not found.")
            click.echo(
                "\rERROR: No raw theme found. Please create the DO_NOT_CHANGE - theme in shopify and restart the process."
            )
            return
        _download_raw_theme(store, theme_name)

        click.echo("Done.")
        click.echo(f"\rTheme Name: {theme_name}")
        click.echo("Commit theme to git...")
        utils.cmd_exec(["git", "add", "."])
        utils.cmd_exec(["git", "commit", "-m", "tes: download theme from shopify"])
        utils.cmd_exec(["git", "push", "-u", "origin"])
        theme_info = _get_theme_info()

    # check if raw theme exists
    click.echo("\rChecking if raw theme exists...", nl=False)
    if not _raw_theme_exists(store, theme_info["theme_name"]):
        click.echo("Not found.")
        click.echo(
            "\rERROR: No raw theme found. Please create the DO_NOT_CHANGE - theme in shopify and restart the process."
        )
        return
    click.echo("Found")

    branches = ["staging"]
    branches.append(
        _get_branch_name_theme(theme_info["theme_name"], theme_info["theme_version"])
    )

    click.echo(f"\rCreating branches: {branches}")
    current_branch = _get_current_branch()
    # check if branches exist and create if not
    for branch in branches:
        if not _branch_exists(branch):
            click.echo(f"\rCreating branch {branch}...", nl=False)
            utils.cmd_exec(["git", "checkout", "-b", branch])
            utils.cmd_exec(["git", "push", "-u", "origin", branch])
            utils.cmd_exec(["git", "checkout", current_branch])
            click.echo(f"Done")

    click.echo("\rBranches created!")

    click.echo("\rShopify theme initialized!")

    # create git branches
    # for branch in BRANCHES:
    #    os.system(f"git checkout -b {branch}")
    #    # push to remote
    #    os.system(f"git push -u origin {branch}")


def ignore_files(src, names):
    prefix = "tmp_new_version"
    if "config" in src:
        return {"settings_data.json"}  # Exclude settings_data.json in config folder
    if src in [
        f"{prefix}/locales",
        f"{prefix}/sections",
        f"{prefix}/templates",
        f"{prefix}/templates/customers",
    ]:
        return {
            name for name in names if name.endswith(".json")
        }  # Exclude all JSON files in templates folder
    return set()


@theme.command()
@click.pass_context
def update(ctx):
    """Update the Shopify theme."""
    config = utils.get_config()
    store = config["shopify"]["store"]
    theme_info = _get_theme_info()
    branch_name_staging = "theme_updater_staging"
    branch_name_temp = "theme_updater_temp"

    # delete temp branches
    if _branch_exists(branch_name_staging):
        utils.cmd_exec(["git", "branch", "-D", branch_name_staging])
    if _branch_exists(branch_name_temp):
        utils.cmd_exec(["git", "branch", "-D", branch_name_temp])

    # create staging branch from current branch
    utils.cmd_exec(["git", "checkout", "-b", branch_name_staging])

    # check if theme branch (old version) exists
    branch_name_theme_version_old = _get_branch_name_theme(
        theme_info["theme_name"], theme_info["theme_version"]
    )

    if not _branch_exists(branch_name_theme_version_old):
        click.echo(f"Branch {branch_name_theme_version_old} does not exist.")
        return

    click.echo("\rBackup raw theme...", nl=False)
    new_theme_info = _backup_raw_theme(store)
    click.echo("\rBackup done.")

    # checkout new branch, copy everything to a temp folder and switch back to main branch
    branch_name_theme_version_new = _get_branch_name_theme(
        new_theme_info["theme_name"], new_theme_info["theme_version"]
    )

    click.echo(f"Old Version: {branch_name_theme_version_old}.")
    click.echo(f"New Version: {branch_name_theme_version_new}.")
    utils.cmd_exec(["git", "checkout", branch_name_theme_version_new])

    # copy everything to a temp folder
    shutil.copytree(
        ".",
        "tmp_new_version",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".git"),
    )
    # create temp branch from old version
    utils.cmd_exec(
        ["git", "checkout", "-b", "theme_updater_temp", branch_name_theme_version_old]
    )

    # copy everything except config/settings_data.json and templates/*.json
    shutil.copytree(
        "tmp_new_version",
        ".",
        dirs_exist_ok=True,
        ignore=ignore_files,
    )
    shutil.rmtree("tmp_new_version")

    # commit changes
    utils.cmd_exec(["git", "add", "."])
    utils.cmd_exec(["git", "commit", "-m", "tes: update theme"])

    # go back to staging branch
    utils.cmd_exec(["git", "checkout", branch_name_staging])
    subprocess.run(["git", "diff", "--stat", branch_name_staging, branch_name_temp])

    click.echo("Shopify theme ready to merge!")
    click.echo("Now you can merge the new version: git merge theme_updater_staging")


def _get_branch_name_theme(theme_name, theme_version):
    return f"raw_themes/{theme_name}-{theme_version}"


def _set_tes_config(config, store):
    # read file config/settings_schema.json
    # get current folder
    if not config.get("shopify"):
        config["shopify"] = {}
    config["shopify"]["store"] = store
    utils.write_config(config)

    # commit and push
    utils.cmd_exec(["git", "add", ".tes.yml"])
    utils.cmd_exec(["git", "commit", "-m", "tes: update tes config"])
    utils.cmd_exec(["git", "push"])


def _branch_exists(branch_name):
    result = utils.cmd_exec(["git", "branch", "--list", branch_name])
    return bool(result.stdout.strip())


def _get_current_branch():
    result = utils.cmd_exec(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise RuntimeError(f"Error getting current branch: {result.stderr.strip()}")


def _get_theme_info(use_current_folder=False):
    # read file config/settings_schema.json
    # get current folder
    folder = utils.WORK_FOLDER
    if use_current_folder:
        folder = os.getcwd()
    if not os.path.exists(os.path.join(folder, "config/settings_schema.json")):
        return None
    with open(os.path.join(folder, "config/settings_schema.json")) as f:
        settings_schema = json.load(f)

    # get by name "theme_info"
    for setting in settings_schema:
        if setting["name"] == "theme_info":
            return setting


def _get_theme_name(store):
    # Run the Shopify CLI command
    result = utils.cmd_exec(["shopify", "theme", "list", "--json", f"--store={store}"])

    # Check for errors
    if result.returncode != 0:
        raise RuntimeError(f"Error running command: {result.stderr.strip()}")

    # Parse the output
    themes = json.loads(result.stdout.strip())
    for theme in themes:
        if theme["name"].startswith("DO_NOT_CHANGE_"):
            return theme["name"]
    return None


def _raw_theme_exists(store, theme_name):
    # Run the Shopify CLI command
    result = utils.cmd_exec(["shopify", "theme", "list", "--json", f"--store={store}"])

    # Check for errors
    if result.returncode != 0:
        raise RuntimeError(f"Error running command: {result.stderr.strip()}")

    # Parse the output
    themes = json.loads(result.stdout.strip())
    for theme in themes:
        if theme["name"] == f"DO_NOT_CHANGE_{theme_name}":
            return True

    return False


def _download_raw_theme(store, theme):
    """download raw theme"""

    # run shopify theme pull
    utils.cmd_exec(["shopify", "theme", "pull", f"--store={store}", f"--theme={theme}"])

    return


def _backup_raw_theme(store):
    """update raw theme"""

    theme_info = _get_theme_info()

    # create raw_themes folder if not exists
    if os.path.exists("raw_themes_tmp"):
        shutil.rmtree("raw_themes_tmp")
    os.mkdir("raw_themes_tmp")

    ## switch to raw_themes folder
    os.chdir("raw_themes_tmp")

    _download_raw_theme(store, f"DO_NOT_CHANGE_{theme_info['theme_name']}")
    new_theme_info = _get_theme_info(use_current_folder=True)

    # switch back to main folder
    os.chdir("..")

    # check if branch for new theme already exists
    new_branch_name = _get_branch_name_theme(
        new_theme_info["theme_name"], new_theme_info["theme_version"]
    )
    if _branch_exists(new_branch_name):
        click.echo("Branch already exists.")
        shutil.rmtree("raw_themes_tmp")
        return new_theme_info

    # overwrite old data
    shutil.copytree(
        "raw_themes_tmp",
        ".",
        dirs_exist_ok=True,
    )
    shutil.rmtree("raw_themes_tmp")

    old_branch_name = _get_current_branch()
    # create new branch
    utils.cmd_exec(["git", "checkout", "-b", new_branch_name])
    utils.cmd_exec(["git", "add", "."])
    utils.cmd_exec(["git", "commit", "-m", "tes: backup theme"])
    utils.cmd_exec(["git", "push", "-u", "origin", new_branch_name])
    utils.cmd_exec(["git", "checkout", old_branch_name])
    return new_theme_info
