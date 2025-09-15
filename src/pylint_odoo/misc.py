import os
import re
import subprocess
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

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
    "17.0",
    "18.0",
    "19.0",
]
DFTL_MANIFEST_VERSION_FORMAT = r"({valid_odoo_versions})\.\d+\.\d+\.\d+$"
TRANSLATION_METHODS = ("_", "_lt")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class StringParseError(TypeError):
    pass


def version_parse(version_str):
    try:
        return tuple(map(int, version_str.split(".")))
    except (ValueError, TypeError):
        return tuple()


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


def full_norm_path(path):
    """Expand paths in all possible ways"""
    return os.path.normpath(os.path.realpath(os.path.abspath(os.path.expanduser(os.path.expandvars(path.strip())))))


@lru_cache(maxsize=256)
def walk_up(path, filenames, top):
    """Look for "filenames" walking up in parent paths of "path"
    but limited only to "top" path
    """
    if full_norm_path(path) == full_norm_path(top):
        return None
    for filename in filenames:
        path_filename = os.path.join(path, filename)
        if os.path.isfile(full_norm_path(path_filename)):
            return path_filename
    return walk_up(os.path.dirname(path), filenames, top)


class InvalidVersion(Exception):
    pass


def version2tuple(version):
    try:
        return tuple(int(i) for i in version.split("."))
    except (ValueError, AttributeError) as exc:
        raise InvalidVersion(
            f"Invalid Version only integers separated by dot was expected. e.g. 19.0.1.0.0 but received {[version]}"
        ) from exc


class InvalidURL(Exception):
    pass


# Based on https://github.com/python-validators/validators/blob/c9585e91f8b409029/src/validators/domain.py#L87-L99
DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-_]{0,61}[a-z]$", re.IGNORECASE)


def validate_url(url):
    if not url:
        raise InvalidURL("Empty URL")
    if re.search(r"\s", url):
        raise InvalidURL("URL must not contain white spaces, they must be encoded")
    try:
        scheme, netloc, _path, _query, _fragment = urlsplit(url)
    except ValueError as ve_exc:
        raise InvalidURL(f"URL invalid: {str(ve_exc)}") from ve_exc

    if scheme not in ("https", "http"):
        raise InvalidURL("URL needs to start with 'http[s]://'")
    if not netloc:
        raise InvalidURL("Invalid URL domain not identified")

    # Based on https://github.com/python-validators/validators/blob/c9585e91f8b409029/src/validators/domain.py#L98
    if re.search(r"__+", netloc):
        raise InvalidURL(f"Domain section must not contain double underscore '__' because of security issues {netloc}")
    try:
        netloc = netloc.encode("idna").decode("utf-8")
    except UnicodeError as err:
        raise InvalidURL(f"Unable to encode/decode domain section {netloc}") from err
    if not DOMAIN_RE.match(netloc):
        raise InvalidURL(f"Domain '{netloc}' contains invalid characters")
    return True


def validate_email(email):
    return EMAIL_RE.match(email) is not None
