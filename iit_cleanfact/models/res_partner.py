from odoo import api, models, fields
import json, requests


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cf_nombre_sat = fields.Char(string='Nombre SAT', default="Consumidor Final") # Nombre SAT

    @api.onchange('vat')
    def onchange_vat(self):
        if (self.vat):

            url = "https://consultareceptores.feel.com.gt/rest/action"

            data = {
                'emisor_codigo': "2459413K",
                'emisor_clave': "46155CE198281D56C1F479082C6946C7",
                'nit_consulta': self.vat
            }

            headers = {
                 'Content-Type': "application/json"
            }


            response = requests.post(url, json=data, headers=headers)

            data = json.loads(response.text)

            self.cf_nombre_sat = data['nombre']

