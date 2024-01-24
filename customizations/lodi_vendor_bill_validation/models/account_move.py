from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_mx_edi_cfdi_request = fields.Selection(selection_add=[('in_invoice', 'Vendor Bill')])
    validation_total = fields.Float(string='Validation Total')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'account.move')],
                                     string='Attachments')

    @api.depends('move_type', 'company_id', 'state', 'invoice_date')
    def _compute_l10n_mx_edi_cfdi_request(self):
        super()._compute_l10n_mx_edi_cfdi_request()
        move_ids = self.filtered(lambda _move: _move.move_type == 'in_invoice')
        move_ids.update({'l10n_mx_edi_cfdi_request': 'in_invoice'})

    def _compute_l10n_mx_edi_cancel(self):
        # OVERRIDDEN
        for move in self:
            if move.l10n_mx_edi_cfdi_uuid and move.move_type != 'in_invoice':
                replaced_move = move.search(
                    [('l10n_mx_edi_origin', 'like', '04|%'),
                     ('l10n_mx_edi_origin', 'like', '%' + move.l10n_mx_edi_cfdi_uuid + '%'),
                     ('company_id', '=', move.company_id.id)],
                    limit=1,
                )
                move.l10n_mx_edi_cancel_invoice_id = replaced_move
            else:
                move.l10n_mx_edi_cancel_invoice_id = None

    @api.depends('restrict_mode_hash_table', 'state')
    def _compute_show_reset_to_draft_button(self):
        # OVERRIDDEN
        self.show_reset_to_draft_button = True
        for move in self.filtered(lambda _move: _move.move_type != 'out_invoice'):
            move.show_reset_to_draft_button = not move.restrict_mode_hash_table and move.state in ('posted', 'cancel')

    def action_post(self):
        bills_to_validate = self.filtered(
            lambda _move: _move.move_type == 'in_invoice' and _move.partner_id.country_id.id == self.env.ref(
                'base.mx').id and _move.partner_id.is_bill_validation is False)
        invalid_bills = bills_to_validate.filtered(lambda
                                                       _move: _move.validation_total != _move.amount_total or _move.l10n_mx_edi_cfdi_uuid is False or _move.l10n_mx_edi_sat_status != 'valid')
        if invalid_bills:
            raise ValidationError(
                _('The following bill(s) can not be validated: %s\n\nThe following are some reasons: \n1. Vendor is not from Mexico\n2. Vendor needs vendor bill validation\n3. Vendors do not have a valid UUID') % (
                    ','.join(invalid_bills.mapped(lambda _invalid_bill: _invalid_bill.ref or _('Without reference')))))
        return super().action_post()
