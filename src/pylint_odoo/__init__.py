__version__ = "8.0.5"

from . import checkers
from .augmentations.main import apply_augmentations
from pylint.lint.message_state_handler import _MessageStateHandler


def is_odoo_message_enabled(odoo_version, msgcode):
    required_odoo_versions = checkers.odoo_addons.OdooAddons.checks_maxmin_odoo_version.get(msgcode) or {}
    odoo_minversion = required_odoo_versions.get("odoo_minversion")
    odoo_maxversion = required_odoo_versions.get("odoo_maxversion")
    if odoo_minversion and odoo_minversion >= odoo_version or odoo_maxversion and odoo_maxversion <= odoo_version:
        return False
    return True


original_is_one_message_enabled = _MessageStateHandler._is_one_message_enabled
def patched_is_one_message_enabled(self, msgid, *args, **kwargs):
    odoo_enabled = True
    valid_odoo_versions = self.linter.config.valid_odoo_versions
    if len(valid_odoo_versions) == 1:
        msgcode = self.linter.msgs_store.message_id_store.get_symbol(msgid)
        try:
            current_odoo_version = tuple(map(int, valid_odoo_versions[0].split(".")))
            odoo_enabled = is_odoo_message_enabled(current_odoo_version, msgcode)
        except ValueError:
            pass
    return odoo_enabled and original_is_one_message_enabled(self, msgid, *args, **kwargs)


def register(linter):
    """Required method to auto register this checker"""
    linter.register_checker(checkers.odoo_addons.OdooAddons(linter))
    linter.register_checker(checkers.vim_comment.VimComment(linter))
    # register any checking fiddlers
    apply_augmentations(linter)
    _MessageStateHandler._is_one_message_enabled = patched_is_one_message_enabled


def get_all_messages():
    """Get all messages of this plugin"""
    all_msgs = {}
    all_msgs.update(checkers.odoo_addons.ODOO_MSGS)
    all_msgs.update(checkers.vim_comment.ODOO_MSGS)
    return all_msgs


def messages2md():
    all_msgs = get_all_messages()
    md_msgs = "Code | Description | short name\n--- | --- | ---"
    for msg_code, (title, name_key, _description) in sorted(all_msgs.items()):
        md_msgs += "\n{} | {} | {}".format(msg_code, title, name_key)
    md_msgs += "\n"
    return md_msgs


def messages2rst():
    """Message list to rst string
    RST table example
    +------------+------------+-----------+
    | Header 1   | Header 2   | Header 3  |
    +============+============+===========+
    | body row 1 | column 12  | column 13 |
    +------------+------------+-----------+
    | body row 2 | column 22  | column 23 |
    +------------+------------+-----------+
    """
    all_msgs = get_all_messages()
    title_list = ["Code", "Description", "Short name"]
    lines = []
    max_col_sizes = [len(item) for item in title_list]
    for msg_code, msg_items in sorted(all_msgs.items()):
        title, name_key, _description = msg_items[0:3]
        line = [item.replace("`", "``") for item in [msg_code, title, name_key]]
        # TODO: consider using enumerate :)
        # pylint: disable=consider-using-enumerate
        for index in range(len(max_col_sizes)):
            if len(line[index]) > max_col_sizes[index]:
                max_col_sizes[index] = len(line[index])
        lines.append(line)

    def rst_spaces(max_col_sizes, line=None, sep="|", fill=" "):
        if line is None:
            line = [""] * len(max_col_sizes)
        return (
            "".join(
                [
                    sep + fill + line[index] + fill * (max_col_sizes[index] - len(line[index]) + 1)
                    for index in range(len(max_col_sizes))
                ]
            )
            + sep
            + "\n"
        )

    rst_msgs = rst_spaces(max_col_sizes, sep="+", fill="-")
    rst_msgs += rst_spaces(max_col_sizes, title_list)
    rst_msgs += rst_spaces(max_col_sizes, sep="+", fill="=")
    rst_msgs += rst_spaces(max_col_sizes, sep="+", fill="-").join([rst_spaces(max_col_sizes, item) for item in lines])
    rst_msgs += rst_spaces(max_col_sizes, sep="+", fill="-")
    return rst_msgs
