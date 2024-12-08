# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from base64 import b64decode
from PyPDF2 import PdfFileReader
import io
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    file_name = fields.Char('File')
    watermark_pdf = fields.Binary('Report Watermark', exportable=False)
    report_header = fields.Html(string='Company Tagline', translate=True, help="Company tagline, which is included in a printed document's header or footer (depending on the selected layout).")
    caption_color_picker = fields.Char("Caption Color Picker")

    @api.onchange('watermark_pdf')
    def _onchange_watermark_page(self):
        if self.watermark_pdf:
            pdf_watermark = b64decode(self.watermark_pdf)
            pdf_content_stream = io.BytesIO(pdf_watermark)
            reader = PdfFileReader(pdf_content_stream)
            if reader.numPages > 1:
                raise UserError(_('Watermark Pdf Contain More Than One Page Please Upload One Page Watermark Pdf File.'))
