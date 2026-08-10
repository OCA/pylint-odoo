import os
import re
import warnings
from pathlib import Path
from types import CodeType
from urllib.parse import urlsplit

import dill
from pylint.lint.expand_modules import _is_ignored_file
from pylint.lint.pylinter import PyLinter

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
    "20.0",
]
DFTL_MANIFEST_VERSION_FORMAT = r"({valid_odoo_versions})\.\d+\.\d+\.\d+$"
TRANSLATION_METHODS = ("_", "_lt")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class StringParseError(TypeError):
    pass


def patch_dill_missing_lnotab():
    """Support pylint --jobs for python 3.15 removing "code.co_lnotab"

    The parallel mode serializes the linter using dill, including the code
    objects of the functions that can not be pickled by reference, but
    dill<=0.4.1 save_code still reads "code.co_lnotab", removed in python 3.15,
    raising AttributeError for any "pylint --jobs" run.

    Feed the original save_code with an empty co_lnotab. It is safe since
    dill._dill._create_code only uses that value to build the code objects of
    payloads serialized by python<3.10, so the workers do not need any patch to
    deserialize them.

    TODO: Remove it when a dill release supports python 3.15
    """
    code_sample = patch_dill_missing_lnotab.__code__
    with warnings.catch_warnings():
        # Deprecated before being removed. hasattr emits DeprecationWarning
        warnings.simplefilter("ignore", DeprecationWarning)
        if hasattr(code_sample, "co_lnotab"):
            return
    original_save_code = dill.Pickler.dispatch[CodeType]
    if getattr(original_save_code, "_pylint_odoo_patch", False):
        return
    try:
        dill.dumps(code_sample)
        return  # New dill release already supporting it
    except AttributeError:
        pass

    class CodeWithLnotab:
        """Expose the attributes of a code object with an empty co_lnotab"""

        def __init__(self, code):
            self._code = code

        def __getattr__(self, name):
            if name == "co_lnotab":
                return b""
            return getattr(self.__dict__["_code"], name)

    def save_code_with_lnotab(pickler, obj):
        original_save_code(pickler, CodeWithLnotab(obj))

    save_code_with_lnotab._pylint_odoo_patch = True
    dill.Pickler.dispatch[CodeType] = save_code_with_lnotab


def patch_recursive_odoo_module_files():
    """Support "pylint --recursive=y" discovering all the files of the Odoo modules

    The upstream file discovery has two gaps running it over an Odoo repository:
     - The .py files inside the subdirectories of a module without "__init__.py"
       are never linted, e.g. migrations/x.y.z/pre-migration.py, because the
       module is expanded as a python package pruning the non-package subtrees
     - A module with a name starting with the name of a previously discovered
       sibling is skipped entirely, e.g. "broken_module2" after "broken_module"

    Replace PyLinter._discover_files applying the upstream fix for the second
    gap, https://github.com/pylint-dev/pylint/pull/10970 released for
    pylint>4.0.7, and yielding the python files of the Odoo modules that are
    not reachable expanding the python packages so "--recursive=y" matches the
    file-by-file way used by pre-commit

    TODO: Keep only the "_odoo_module_extra_files" part when the minimum
    supported pylint release includes the pull request 10970
    """
    original_discover_files = PyLinter._discover_files
    if getattr(original_discover_files, "_pylint_odoo_patch", False):
        return

    def _odoo_module_extra_files(linter, package_dir):
        """Yield the python files of an Odoo module not reachable expanding the
        python packages, e.g. migrations/x.y.z/pre-migration.py since the
        subdirectory does not have a "__init__.py" file
        """
        if not any(os.path.isfile(os.path.join(package_dir, manifest)) for manifest in MANIFEST_FILES):
            return
        reachable = {package_dir}
        skip_subtrees = []
        for root, _, files in os.walk(package_dir):
            if any(root.startswith(skipped) for skipped in skip_subtrees):
                continue
            if _is_ignored_file(root, linter.config.ignore, linter.config.ignore_patterns, linter.config.ignore_paths):
                skip_subtrees.append(root + os.sep)
                continue
            if root == package_dir:
                continue
            if os.path.dirname(root) in reachable and "__init__.py" in files:
                # Already linted expanding the packages of the module
                reachable.add(root)
                continue
            yield from (os.path.join(root, file) for file in files if file.endswith((".py", ".pyi")))

    def _discover_files(self, files_or_modules):
        for something in files_or_modules:
            if os.path.isdir(something) and not os.path.isfile(os.path.join(something, "__init__.py")):
                skip_subtrees = []
                for root, _, files in os.walk(something):
                    if any(root.startswith(skipped) for skipped in skip_subtrees):
                        # Skip subtree of already discovered package.
                        continue
                    if _is_ignored_file(
                        root, self.config.ignore, self.config.ignore_patterns, self.config.ignore_paths
                    ):
                        skip_subtrees.append(root + os.sep)
                        continue
                    if "__init__.py" in files:
                        skip_subtrees.append(root + os.sep)
                        yield root
                        yield from _odoo_module_extra_files(self, root)
                    else:
                        yield from (os.path.join(root, file) for file in files if file.endswith((".py", ".pyi")))
            else:
                yield something
                if os.path.isdir(something):
                    yield from _odoo_module_extra_files(self, something)

    _discover_files._pylint_odoo_patch = True
    PyLinter._discover_files = _discover_files


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


# Cache of the top level path resolved for each path already visited and
# set of the top level paths already found containing a ".git" entry
_top_path_cache = {}
_known_top_paths = set()


def top_path(path):
    """Get the top level path based on the first parent path containing a ".git"
    entry (a directory for regular repositories or a file for submodules and worktrees)
    But if it is not a git repository so the top is the drive name
    e.g. / or C:\\
    The values are cached and the children paths of a top level path already found
    re-use it directly based on the path prefix so they are resolved without
    checking ".git" for each parent path again
    """
    top = _top_path_cache.get(path)
    if top is not None:
        return top
    path_obj = Path(path)
    for known_top_path in _known_top_paths:
        if path_obj.is_relative_to(known_top_path):
            _top_path_cache[path] = known_top_path
            return known_top_path
    if (path_obj / ".git").exists():
        _known_top_paths.add(path)
        _top_path_cache[path] = path
        return path
    parent_path = path_obj.parent
    if parent_path == path_obj:
        top = path_obj.root or path_obj.drive
    else:
        top = top_path(str(parent_path))
    _top_path_cache[path] = top
    return top


def full_norm_path(path):
    """Expand paths in all possible ways"""
    return Path(os.path.expandvars(str(path).strip())).expanduser().resolve()


# Cache of the results already resolved by path, filenames and top and the
# parent paths where one of the filenames was already found by filenames
_walk_up_cache = {}
_known_walk_up_dirs = {}


def walk_up(path, filenames, top):
    """Look for "filenames" walking up in parent paths of "path"
    but limited only to "top" path
    The results are cached and the children paths of a parent path where one of
    the filenames was already found re-use it directly without checking the
    filesystem for each parent path again
    """
    cache_key = (path, filenames, top)
    try:
        return _walk_up_cache[cache_key]
    except KeyError:
        pass
    known_dirs = _known_walk_up_dirs.setdefault(filenames, {})
    path_obj = Path(path)
    result = None
    for parent_path in (path_obj, *path_obj.parents):
        result = known_dirs.get((str(parent_path), top))
        if result is not None:
            break
    if result is None:
        top_norm_path = full_norm_path(top)
        current_path = path_obj
        while full_norm_path(current_path) != top_norm_path:
            for filename in filenames:
                path_filename = current_path / filename
                if full_norm_path(path_filename).is_file():
                    result = str(path_filename)
                    known_dirs[(str(current_path), top)] = result
                    break
            if result is not None or current_path.parent == current_path:
                break
            current_path = current_path.parent
    _walk_up_cache[cache_key] = result
    return result


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
        raise InvalidURL(f"Domain {netloc!r} contains invalid characters")
    return True


def validate_email(email):
    return EMAIL_RE.match(email) is not None
