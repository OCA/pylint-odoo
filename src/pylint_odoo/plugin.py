from . import checkers
from .augmentations.main import apply_augmentations


def register(linter):
    """Required method to auto register this checker"""
    linter.register_checker(checkers.odoo_addons.OdooAddons(linter))
    linter.register_checker(checkers.vim_comment.VimComment(linter))
    linter.register_checker(checkers.custom_logging.CustomLoggingChecker(linter))

    # register any checking fiddlers
    apply_augmentations(linter)


def get_all_messages():
    """Get all messages of this plugin"""
    all_msgs = {}
    all_msgs.update(checkers.odoo_addons.ODOO_MSGS)
    all_msgs.update(checkers.vim_comment.ODOO_MSGS)
    all_msgs.update(checkers.custom_logging.ODOO_MSGS)
    return all_msgs


def messages2md():
    all_msgs = get_all_messages()
    md_msgs = "Short Name | Description | Code\n--- | --- | ---"
    for msg_code, (title, name_key, _description) in sorted(all_msgs.items(), key=lambda v: v[1][1]):
        md_msgs += f"\n{name_key} | {title} | {msg_code}"
    md_msgs += "\n"
    return md_msgs
