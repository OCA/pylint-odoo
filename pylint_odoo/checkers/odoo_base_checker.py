from __future__ import annotations

import pylint
from pylint.checkers import BaseChecker

from .. import misc


class OdooBaseChecker(BaseChecker):
    # checks_maxmin_odoo_version = {
    #   check-code: {
    #       "odoo_minversion": "14.0",
    #       "odoo_maxversion": "15.0",
    #   }
    checks_maxmin_odoo_version: dict[str, str] = {}

    def msgid_or_symbol2symbol(self, msgid_or_symbol):
        try:
            msgid = self.linter.msgs_store.message_id_store.get_active_msgids(msgid_or_symbol)[0]
            return self.linter.msgs_store.message_id_store.get_symbol(msgid)
        except (pylint.exceptions.UnknownMessageError, IndexError):
            return None

    def is_odoo_message_enabled(self, msgid):
        valid_odoo_versions = self.linter.config.valid_odoo_versions
        if len(valid_odoo_versions) != 1:
            # It should be defined only one version
            return True
        msg_symbol = self.msgid_or_symbol2symbol(msgid)
        if msg_symbol is None:
            return True
        odoo_version = valid_odoo_versions[0]
        required_odoo_versions = self.checks_maxmin_odoo_version.get(msg_symbol) or {}
        odoo_minversion = required_odoo_versions.get("odoo_minversion") or misc.DFTL_VALID_ODOO_VERSIONS[0]
        odoo_maxversion = required_odoo_versions.get("odoo_maxversion") or misc.DFTL_VALID_ODOO_VERSIONS[-1]
        return (
            misc.version_parse(odoo_minversion)
            <= misc.version_parse(odoo_version)
            <= misc.version_parse(odoo_maxversion)
        )

    def add_message(self, msgid, *args, **kwargs):
        """Emit translation-not-lazy instead of logging-not-lazy"""
        if not self.is_odoo_message_enabled(msgid):
            return
        return super().add_message(msgid, *args, **kwargs)
