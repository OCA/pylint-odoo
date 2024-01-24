import base64
import logging

from lxml import etree
from lxml.objectify import fromstring

from odoo import fields, models, Command, _
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

_TASA_TAX_TYPE = 'Tasa'


class VendorBillAttachmentWizard(models.TransientModel):
    _name = 'vendor.bill.attachment.wizard'
    _description = 'Wizard to attach bill xml files'

    journal_id = fields.Many2one(comodel_name='account.journal', string='Journal', required=True,
                                 domain=lambda _self: [('type', '=', 'purchase'),
                                                       ('company_id', '=', _self.env.company.id)])
    account_id = fields.Many2one(comodel_name='account.account', string='Account', required=True,
                                 domain=lambda _self: [('company_id', '=', _self.env.company.id)])
    attachment_ids = fields.Many2many(
        'ir.attachment', 'vendor_bill_attachment_ir_attachments_rel',
        'wizard_id', 'attachment_id', string='Attachments')

    def action_process(self):
        return self._process_xml_files()

    def _build_bill_values(self, attachment_ids):
        xml_bills = []
        for attachment in attachment_ids:
            cfdi_data = base64.decodebytes(attachment.with_context(bin_size=False).datas)
            cfdi_node = VendorBillAttachmentWizard._decode_cfdi(attachment, cfdi_data)
            xml_bills.append(cfdi_node)
        return xml_bills

    def _validate_vats(self, xml_bills):
        supplier_vat_dict = {bill.get('supplier_rfc'): bill.get('attachment').name or '' for bill in xml_bills}
        supplier_vats = supplier_vat_dict.keys()
        partner_ids = self.env['res.partner'].search([('vat', 'in', list(supplier_vats))])
        existing_vats = partner_ids.mapped('vat')
        not_existing_vats = list(set(supplier_vats).difference(existing_vats))
        if not_existing_vats:
            not_existing_vats_msj = [_('\nVAT: %s from file: %s', vat, supplier_vat_dict.get(vat)) for vat in
                                     not_existing_vats]
            raise ValidationError(_('The following VATs do not exist %s') % (','.join(not_existing_vats_msj)))
        return partner_ids

    def _validate_bills_with_sat(self, bills):
        for bill_values in bills:
            try:
                status = self.env['account.edi.format']._l10n_mx_edi_get_sat_status(bill_values.get('supplier_rfc'),
                                                                                    bill_values.get('customer_rfc'),
                                                                                    bill_values.get('amount_total'),
                                                                                    bill_values.get('uuid'))
                if status != 'Vigente':
                    raise ValidationError(_("Bill %(msg)s has an invalid status", msg=str(bill_values.get('folio'))))
            except Exception as e:
                raise ValidationError(_("Failure during validation of the SAT status: %(msg)s", msg=str(e)))

    def _verify_synchronized_bills(self, xml_bills):
        bill_ids = self.env['account.move'].search(
            [('move_type', '=', 'in_invoice'), ('ref', 'in', [bill.get('folio') for bill in xml_bills]),
             ('partner_id.vat', 'in', [bill.get('supplier_rfc') for bill in xml_bills])])

        synchronized_bills = bill_ids.filtered(
            lambda _bill: _bill.state != 'draft' and _bill.l10n_mx_edi_sat_status != 'undefined')
        if synchronized_bills:
            raise ValidationError(_('The following Bills have been already synchronized: %s') % (
                ','.join(synchronized_bills.mapped('ref'))))
        return bill_ids

    def _update_existing_bills(self, xml_bills, bill_ids):
        for xml in xml_bills:
            bill_id = bill_ids.filtered(
                lambda _bill: _bill.state == 'draft' and _bill.ref == xml.get(
                    'folio') and _bill.partner_id.vat == xml.get('supplier_rfc'))
            bill_id.edi_document_ids.unlink()
            bill_id.update({'validation_total': xml.get('amount_total')})

    def _create_new_bills(self, bill_ids, xml_bills, partner_ids, wizard):
        not_existing_bills = [xml for xml in xml_bills if xml.get('folio') not in bill_ids.mapped('ref')]

        return self.env['account.move'].create([{
            'move_type': 'in_invoice',
            'partner_id': partner_ids.filtered(
                lambda _partner: _partner.vat == bill_values.get('supplier_rfc'))[:1].id,
            'ref': bill_values.get('folio'),
            'validation_total': bill_values.get('amount_total'),
            'journal_id': wizard.journal_id.id,
            'invoice_line_ids': self._prepare_invoice_line_ids(bill_values.get('invoice_lines'),
                                                               wizard.account_id.id),
        } for bill_values in not_existing_bills])

    def _update_l10n_mx_edi_bill_fields(self, bill_ids, xml_bills):
        for bill in bill_ids:
            xml_bill_values = \
                list(filter(lambda _bill: _bill.get('folio') == bill.ref and _bill.get('supplier_rfc'), xml_bills))[0]
            attachment = xml_bill_values.get('attachment')
            bill.update({'validation_total': xml_bill_values.get('amount_total'),
                         'l10n_mx_edi_cfdi_uuid': xml_bill_values.get('uuid'),
                         'l10n_mx_edi_sat_status': 'valid',
                         'invoice_date': fields.Date.from_string(xml_bill_values.get('stamp_date'))})
            bill.edi_document_ids = self.env['account.edi.document'].create({
                'move_id': bill.id,
                'edi_format_id': self.env.ref('l10n_mx_edi.edi_cfdi_3_3').id,
                'state': 'sent',
                'attachment_id': attachment.id,
            })
            bill.with_context(no_new_invoice=True).message_post(
                body=_("The CFDI document was successfully created."),
                attachment_ids=attachment.ids,
            )

    def _process_xml_files(self):
        for wizard in self:
            xml_bills = self._build_bill_values(wizard.attachment_ids)

            partner_ids = self._validate_vats(xml_bills)

            self._validate_bills_with_sat(xml_bills)

            bill_ids = self._verify_synchronized_bills(xml_bills)

            self._update_existing_bills(xml_bills, bill_ids)

            bill_ids |= self._create_new_bills(bill_ids, xml_bills, partner_ids, wizard)

            self._update_l10n_mx_edi_bill_fields(bill_ids, xml_bills)

            self._validate_bills_with_sat([{'supplier_rfc': bill.partner_id.vat, 'customer_rfc': self.env.company.vat,
                                            'amount_total': bill.validation_total, 'uuid': bill.l10n_mx_edi_cfdi_uuid,
                                            'folio': bill.ref}
                                           for bill in bill_ids])

            return self._view_processed_bills(bill_ids.ids)

    def _view_processed_bills(self, bill_ids):
        return {
            'name': _('Bills'),
            'view_mode': 'tree, form',
            'views': [(False, 'tree'), (False, 'form')],
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', bill_ids)],
        }

    def _prepare_invoice_line_ids(self, invoice_lines, account_id):
        tax_list = [line.get('taxes') for line in invoice_lines if line.get('taxes')]
        tax_ids = self._fetch_tax_ids(tax_list)

        return [Command.create({
            'name': line.get('name'),
            'account_id': account_id,
            'discount': line.get('discount_percentage'),
            'quantity': line.get('quantity'),
            'price_unit': line.get('price_unit'),
            'tax_ids': self._prepare_move_line_taxes(line.get('taxes'), tax_ids)
        }) for line in invoice_lines]

    def _fetch_tax_ids(self, tax_list):

        def _get_tax_attr_value(tax_list, attr):
            tax_values = []
            for item in tax_list:
                for tax in item:
                    tax_values.append(tax.get(attr))
            return tax_values

        if not tax_list:
            return None
        tax_codes = _get_tax_attr_value(tax_list, 'code')
        tax_amounts = _get_tax_attr_value(tax_list, 'amount')

        return self.env['account.tax'].search(
            [('type_tax_use', '=', 'purchase'), ('amount_type', 'in', ['percent', 'fixed']), ('code', 'in', tax_codes),
             ('amount', 'in', tax_amounts), ('company_id', '=', self.env.company.id)])

    def _prepare_move_line_taxes(self, line_taxes, tax_ids):
        tax_list = []
        for tax in line_taxes:
            tax_id = tax_ids.filtered(lambda _tax: _tax.code == tax.get('code') and _tax.amount_type == tax.get(
                'type') and _tax.amount == tax.get('amount'))
            if tax_id:
                tax_list.append(Command.link(tax_id[0].id))

        return tax_list

    @staticmethod
    def _decode_cfdi(attachment, cfdi_data=None, ):

        def get_node(cfdi_node, attribute, namespaces):
            if hasattr(cfdi_node, 'Complemento'):
                node = cfdi_node.Complemento.xpath(attribute, namespaces=namespaces)
                return node[0] if node else None
            else:
                return None

        if not cfdi_data:
            return {}

        try:
            cfdi_node = fromstring(cfdi_data)
            emisor_node = cfdi_node.Emisor
            receptor_node = cfdi_node.Receptor
        except etree.XMLSyntaxError:
            # Not an xml
            return {}
        except AttributeError:
            # Not a CFDI
            return {}

        tfd_node = get_node(
            cfdi_node,
            'tfd:TimbreFiscalDigital[1]',
            {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'},
        )

        return {
            'attachment': attachment,
            'uuid': ({} if tfd_node is None else tfd_node).get('UUID'),
            'supplier_rfc': emisor_node.get('Rfc', emisor_node.get('rfc')),
            'customer_rfc': receptor_node.get('Rfc', receptor_node.get('rfc')),
            'amount_total': cfdi_node.get('Total', cfdi_node.get('total')),
            'folio': cfdi_node.get('Folio', cfdi_node.get('folio', '')),
            'emission_date_str': cfdi_node.get('fecha', cfdi_node.get('Fecha', '')).replace('T', ' '),
            'stamp_date': tfd_node is not None and tfd_node.get('FechaTimbrado', '').replace('T', ' '),
            'invoice_lines': VendorBillAttachmentWizard._prepare_invoice_lines(cfdi_node),
        }

    @staticmethod
    def _prepare_invoice_lines(cfdi_node=None):
        if cfdi_node is None:
            return []

        lines = []
        for line in cfdi_node.Conceptos.Concepto:
            taxes = []
            try:
                VendorBillAttachmentWizard._add_taxes_data(line.Impuestos.Traslados.getiterator(), 'Traslados', taxes)
                VendorBillAttachmentWizard._add_taxes_data(line.Impuestos.Retenciones.getiterator(), 'Retenciones',
                                                           taxes, -1)
            except AttributeError as exception:
                logger.warning(exception)

            price_unit = line.get('ValorUnitario')
            discount_amount = line.get('Descuento', 0)

            discount_percentage = float(discount_amount) * 100 / float(price_unit)

            lines.append(
                {'name': line.get('Descripcion'), 'discount_percentage': discount_percentage, 'quantity': line.get('Cantidad'),
                 'price_unit': price_unit, 'taxes': taxes})

        return lines

    @staticmethod
    def _add_taxes_data(tax_iterator, filter, taxes, sign=1.0):
        for tax in [node for node in tax_iterator if
                    node.tag.find(filter) == -1]:
            amount_type = 'percent' if tax.get('TipoFactor') == 'Tasa' else 'fixed'
            tax_amount = float(tax.get('TasaOCuota')) * sign
            amount = tax_amount * 100 if tax.get('TipoFactor') == 'Tasa' else tax_amount

            taxes.append({'code': tax.get('Impuesto'), 'type': amount_type,
                          'amount': amount})
