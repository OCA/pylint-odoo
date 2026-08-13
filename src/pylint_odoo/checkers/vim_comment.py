import tokenize

from pylint.checkers import BaseTokenChecker

from .odoo_base_checker import OdooBaseChecker

ODOO_MSGS = {
    # C->convention R->refactor W->warning E->error F->fatal
    "W8202": ("Use of vim comment", "use-vim-comment", "Better using local vim configuration file"),
}


class VimComment(OdooBaseChecker, BaseTokenChecker):
    name = "odoolint"
    msgs = ODOO_MSGS

    def open(self):
        """Compute once per run if the only message of this class is disabled
        globally (config/CLI) or not applicable to the valid_odoo_versions configured
        """
        super().open()
        self._is_check_enabled = self.linter.is_message_enabled("use-vim-comment") and self.is_odoo_message_enabled(
            "W8202"
        )

    def is_vim_comment(self, comment):
        return comment.strip("# ").lower().startswith("vim:")

    def process_tokens(self, tokens):
        # Re-checked per module so module-level "disable=use-vim-comment" pragmas skip the loop too
        if not self._is_check_enabled or not self.linter.is_message_enabled("use-vim-comment"):
            return
        for tok_type, token_content, start_line_col, _end_line_col, _line_content in tokens:
            if tokenize.COMMENT == tok_type:
                line_num = start_line_col[0]
                if self.is_vim_comment(token_content):
                    self.add_message("use-vim-comment", line=line_num)
