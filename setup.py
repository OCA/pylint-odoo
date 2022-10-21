import re
from os.path import dirname, join

from setuptools import setup

try:
    from pbr import git
except ImportError:
    git = None


def generate_changelog():
    fname = "ChangeLog"
    if not git:
        changelog_str = '# ChangeLog was not generated. You need to install "pbr"'
        with open(fname, "w", encoding="UTF-8") as fchg:
            fchg.write(changelog_str)
        return changelog_str
    changelog = git._iter_log_oneline()
    changelog = git._iter_changelog(changelog)
    git.write_git_changelog(changelog=changelog)
    # git.generate_authors()
    return read(fname)


def generate_dependencies():
    return read("requirements.txt").splitlines()


def read(*names, **kwargs):
    with open(join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")) as file_obj:
        return file_obj.read()


def generage_long_description():
    long_description = "{}\n{}".format(
        # re.compile(".*\(start-badges\).*^.*\(end-badges\)", re.M | re.S).sub("", read("README.md")),
        read("README.md"),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", generate_changelog()),
    )
    return long_description


setup(
    long_description=generage_long_description(),
    install_requires=generate_dependencies(),
)
