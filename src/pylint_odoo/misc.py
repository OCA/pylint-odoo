import os
import subprocess
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

MANIFEST_DATA_KEYS = ["data", "demo", "demo_xml", "init_xml", "test", "update_xml"]

README_FILES = ["README.rst", "README.md", "README.txt"]

MANIFEST_FILES = [
    "__manifest__.py",
    "__odoo__.py",
    "__openerp__.py",
    "__terp__.py",
]
DFTL_README_TMPL_URL = "https://github.com/OCA/maintainer-tools/blob/master/template/module/README.rst"
DFTL_VALID_ODOO_VERSIONS = [
    "4.2",
    "5.0",
    "6.0",
    "6.1",
    "7.0",
    "8.0",
    "9.0",
    "10.0",
    "11.0",
    "12.0",
    "13.0",
    "14.0",
    "15.0",
    "16.0",
]
DFTL_MANIFEST_VERSION_FORMAT = r"({valid_odoo_versions})\.\d+\.\d+\.\d+$"


class StringParseError(TypeError):
    pass


def version_parse(version_str):
    return tuple(map(int, version_str.split(".")))


def get_plugin_msgs(pylint_run_res):
    """Get all message of this pylint plugin.
    :param pylint_run_res: Object returned by pylint.run method.
    :return: List of strings with message name.
    """

    all_plugin_msgs = []
    for key, message in pylint_run_res.linter.msgs_store._messages_definitions.items():
        checker_name = message.msgid
        if checker_name == "odoolint":
            all_plugin_msgs.append(key)
    return all_plugin_msgs


@contextmanager
def chdir(directory):
    """Change the current directory similar to command 'cd directory'
    but remembering the previous value to be revert at final
    Similar to run 'original_dir=$(pwd) && cd odoo && cd ${original_dir}'
    """
    original_dir = os.getcwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(original_dir)


@lru_cache(maxsize=256)
def top_path(path):
    """Get the top level path based on git
    But if it is not a git repository so the top is the drive name
    e.g. / or C:\\
    It is using lru_cache in order to re-use top level path values
    if multiple files are sharing the same path
    """
    try:
        with chdir(path):
            return subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode(sys.stdout.encoding).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        path = Path(path)
        return path.root or path.drive


@lru_cache(maxsize=256)
def walk_up(path, filenames, top):
    """Look for "filenames" walking up in parent paths of "path"
    but limited only to "top" path
    """
    if path == top:
        return None
    for filename in filenames:
        path_filename = os.path.join(path, filename)
        if os.path.isfile(path_filename):
            return path_filename
    return walk_up(os.path.dirname(path), filenames, top)
