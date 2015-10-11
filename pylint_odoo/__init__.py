
from . import checkers
from . augmentations.main import apply_augmentations


def register(linter):
    """Required method to auto register this checker"""
    linter.register_checker(checkers.modules_odoo.ModuleChecker(linter))
    linter.register_checker(checkers.no_modules.NoModuleChecker(linter))
    linter.register_checker(checkers.format.FormatChecker(linter))

    # register any checking fiddlers
    apply_augmentations(linter)


def get_all_messages():
    """Get all messages of this plugin"""
    all_msgs = {}
    all_msgs.update(checkers.modules_odoo.ODOO_MSGS)
    all_msgs.update(checkers.no_modules.ODOO_MSGS)
    all_msgs.update(checkers.format.ODOO_MSGS)
    return all_msgs


def messages2md():
    all_msgs = get_all_messages()
    md_msgs = 'Code | Description | short name\n--- | --- | ---'
    for msg_code, (title, name_key, description) in \
                            sorted(all_msgs.iteritems()):
            md_msgs += "\n{0} | {1} | {2}".format(msg_code, title, name_key)
    md_msgs += '\n'
    return md_msgs
