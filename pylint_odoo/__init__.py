
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
    for msg_code, (title, name_key, description) in \
            sorted(all_msgs.iteritems()):
        line = [item.replace('`', '``')
                for item in [msg_code, title, name_key]]
        for index in range(len(max_col_sizes)):
            if len(line[index]) > max_col_sizes[index]:
                max_col_sizes[index] = len(line[index])
        lines.append(line)

    def rst_spaces(max_col_sizes, line=None, sep='|', fill=' '):
        if line is None:
            line = [''] * len(max_col_sizes)
        return ''.join(
            [sep + fill + line[index] +
             fill * (max_col_sizes[index] - len(line[index]) + 1)
             for index in range(len(max_col_sizes))]) + sep + '\n'
    rst_msgs = rst_spaces(max_col_sizes, sep='+', fill='-')
    rst_msgs += rst_spaces(max_col_sizes, title_list)
    rst_msgs += rst_spaces(max_col_sizes, sep='+', fill='=')
    rst_msgs += rst_spaces(max_col_sizes, sep='+', fill='-').join(
        [rst_spaces(max_col_sizes, item) for item in lines])
    rst_msgs += rst_spaces(max_col_sizes, sep='+', fill='-')
    rst_msgs = rst_msgs
    return rst_msgs
