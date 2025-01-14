import os
import subprocess
import yaml

WORK_FOLDER = os.getcwd()
CONFIG_FILE = os.path.join(WORK_FOLDER, ".tes.yml")
CONFIG_VERSION = "1.0.0"


def _create_tes_yml():
    # create .tes.yml file
    basic_config = {
        "cli_version": CONFIG_VERSION,
    }

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(basic_config, f)


def get_config():
    if not os.path.exists(CONFIG_FILE):
        _create_tes_yml()

    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    return config


def write_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f)


def cmd_exec(commands: list):
    return subprocess.run(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
