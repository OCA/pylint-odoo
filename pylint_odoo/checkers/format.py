
import os
import tokenize
from sys import platform

from .. import settings
from ..misc import PylintOdooTokenChecker

ODOO_MSGS = {
    # C->convention R->refactor W->warning E->error F->fatal

    'C%d01' % settings.BASE_FORMAT_ID: (
        'No UTF-8 coding comment found: '
        'Use `# coding: utf-8` or `# -*- coding: utf-8 -*-`',
        'no-utf8-coding-comment',
        settings.DESC_DFLT,
        {"maxversion": (3, 0)},
    ),
    'C%d02' % settings.BASE_FORMAT_ID: (
        'UTF-8 coding is not necessary',
        'unnecessary-utf8-coding-comment',
        settings.DESC_DFLT,
        {"minversion": (3, 0)},
    ),
    'W%d01' % settings.BASE_FORMAT_ID: (
        'You have a python file with execution permissions but you don\'t '
        'have an interpreter magic comment, or a magic comment but no '
        'execution permission. '
        'If you really needs a execution permission then add a magic comment '
        '( https://en.wikipedia.org/wiki/Shebang_(Unix) ). '
        'If you don\'t needs a execution permission then remove it with: '
        'chmod -x %s',
        'incoherent-interpreter-exec-perm',
        settings.DESC_DFLT
    ),
    'W%d02' % settings.BASE_FORMAT_ID: (
        'Use of vim comment',
        'use-vim-comment',
        settings.DESC_DFLT
    ),
}

MAGIC_COMMENT_CODING = 1
MAGIC_COMMENT_ENCODING = 2
MAGIC_COMMENT_INTERPRETER = 3
MAGIC_COMMENT_CODING_UTF8 = 4
NO_IDENTIFIED = -1


class FormatChecker(PylintOdooTokenChecker):

    name = settings.CFG_SECTION
    msgs = ODOO_MSGS
    odoo_check_versions = {
        'no-utf8-coding-comment': {
            'min_odoo_version': '4.2',
            'max_odoo_version': '10.0',
        },
        'unnecessary-utf8-coding-comment': {
            'min_odoo_version': '11.0',
        },
    }

    def get_magic_comment_type(self, comment, line_num):
        if line_num >= 1 and line_num <= 2:
            if "#!" == comment[:2]:
                return MAGIC_COMMENT_INTERPRETER
            elif "# -*- coding: " in comment or "# coding: " in comment:
                if "# -*- coding: utf-8 -*-" in comment \
                   or "# coding: utf-8" in comment:
                    return MAGIC_COMMENT_CODING_UTF8
                return MAGIC_COMMENT_CODING
            elif "# -*- encoding: " in comment:
                return MAGIC_COMMENT_ENCODING
        return NO_IDENTIFIED

    def is_vim_comment(self, comment):
        return True if comment.strip('# ').lower().startswith('vim:') \
            else False

    def process_tokens(self, tokens):
        tokens_identified = {}
        for idx, (tok_type, token_content,
                  start_line_col, end_line_col,
                  line_content) in enumerate(tokens):
            if tokenize.COMMENT == tok_type:
                line_num = start_line_col[0]
                magic_comment_type = self.get_magic_comment_type(
                    token_content, line_num)
                if magic_comment_type != NO_IDENTIFIED:
                    tokens_identified[magic_comment_type] = [
                        token_content, line_num]
                elif self.is_vim_comment(token_content):
                    self.add_message('use-vim-comment', line=line_num)
        if not tokens_identified.get(MAGIC_COMMENT_CODING_UTF8) and \
           not os.path.basename(self.linter.current_file) == '__init__.py':
            self.add_message('no-utf8-coding-comment', line=1)
        if (tokens_identified.get(MAGIC_COMMENT_CODING_UTF8)):
            self.add_message('unnecessary-utf8-coding-comment', line=1)
        access_x = os.access(self.linter.current_file, os.X_OK)
        interpreter_content, line_num = tokens_identified.get(
            MAGIC_COMMENT_INTERPRETER, ['', 0])
        if (not platform.startswith('win') and
                bool(interpreter_content) != access_x):
            self.add_message(
                'incoherent-interpreter-exec-perm',
                line=line_num, args=(
                    os.path.basename(self.linter.current_file)))
