#!/usr/bin/env python3
import os

import cloudinary
from cloudinary import api

from cloudinary_cli.defaults import CLOUDINARY_CLI_CONFIG_FILE, OLD_CLOUDINARY_CLI_CONFIG_FILE, logger
from cloudinary_cli.utils.json_utils import write_json_to_file, read_json_from_file
from cloudinary_cli.utils.utils import log_exception


def load_config():
    if not os.path.exists(CLOUDINARY_CLI_CONFIG_FILE) or os.path.getsize(CLOUDINARY_CLI_CONFIG_FILE) < 1:
        return {}

    return read_json_from_file(CLOUDINARY_CLI_CONFIG_FILE)


def save_config(config):
    _verify_file_path(CLOUDINARY_CLI_CONFIG_FILE)
    write_json_to_file(config, CLOUDINARY_CLI_CONFIG_FILE)


def update_config(new_config):
    curr_config = load_config()
    curr_config.update(new_config)
    save_config(curr_config)


def remove_config_keys(*keys):
    curr_config = load_config()
    not_found = []
    for key in keys:
        if not curr_config.pop(key, None):
            not_found.append(key)

    save_config(curr_config)

    return not_found


def refresh_cloudinary_config(cloudinary_url):
    os.environ.update({'CLOUDINARY_URL': cloudinary_url})
    cloudinary.reset_config()


def verify_cloudinary_url(cloudinary_url):
    refresh_cloudinary_config(cloudinary_url)
    try:
        api.ping()
    except Exception as e:
        log_exception(e, f"Invalid Cloudinary URL: {cloudinary_url}")
        return False
    return True


def migrate_old_config():
    """
    Migrate old config file (if exists) to new location
    """
    if not os.path.exists(OLD_CLOUDINARY_CLI_CONFIG_FILE):
        return

    try:
        old_config = read_json_from_file(OLD_CLOUDINARY_CLI_CONFIG_FILE)
    except Exception:
        logger.error(f"Unable to parse old Cloudinary config file: {OLD_CLOUDINARY_CLI_CONFIG_FILE}, "
                     f"please fix or remove it")
        raise

    new_config = load_config()
    new_config.update(old_config)
    save_config(new_config)

    os.remove(OLD_CLOUDINARY_CLI_CONFIG_FILE)


def initialize():
    migrate_old_config()


def _verify_file_path(file):
    os.makedirs(os.path.dirname(file), exist_ok=True)
