from odoo import api, models, fields
from odoo.exceptions import ValidationError
import xml.etree.ElementTree as ET
import urllib, json, requests
from ..controllers.fel import controllerfel as confel


class account_move(models.Model):
    _inherit = "account.move"

    fel_uuid = fields.Char(string='Autorizacion FEL Infile')  # registro electronico infile
    fel_serie = fields.Char(string='Serie FEL')  # Serie FEL
    fel_numero = fields.Char(string='Numero FEL')  # Numero Fel
    fel_certificado = fields.Boolean(string='Certificado electronicamente', default=False) # Si esta certificado
    fel_fecha = fields.Date(string='Fecha de factura firmada') # Para registro

    @api.model
    def create(self,vals):
        res = super(account_move, self).create(vals)

        if (res.move_type == "out_refund") and (res.state != "draft"):

            fel_Xml = confel.genxml(res,'NCRE')


            data = confel.firmafel(res,fel_Xml)

            if not data['resultado']:
                errores = data['descripcion_errores']
                raise ValidationError(errores[0]['mensaje_error'])

            # ET.ElementTree(fel_Xml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/" + data['uuid'] + ".xml")
            ET.ElementTree(fel_Xml).write("/opt/odoo/fel/" + data['uuid'] + ".xml",encoding="unicode")

            notacreada = self.env['account.move'].browse(res.id)

            res.fel_uuid = data['uuid']
            res.fel_serie = data['serie']
            res.fel_numero = data['numero']
            res.fel_certificado = True
            res.fel_fecha = res.create_date

        return res

    def action_post(self):
        res = super(account_move, self).action_post()
        if (self.move_type == "out_invoice"):

            fel_Xml = confel.genxml(self,'FACT')

            ET.ElementTree(fel_Xml).write("/opt/odoo/fel/pararevisar.xml",encoding="unicode")
            # ET.ElementTree(fel_Xml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/pararevisar.xml", encoding="unicode")

            data = confel.firmafel(self,fel_Xml)


            print(data)
            if not data['resultado']:
                errores = data['descripcion_errores']
                raise ValidationError(errores[0]['mensaje_error'])

            # ET.ElementTree(fel_Xml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/" + data['uuid'] + ".xml")
            ET.ElementTree(fel_Xml).write("/opt/odoo/fel/" + data['uuid'] + ".xml",encoding="unicode")

            self.fel_uuid = data['uuid']
            self.fel_serie = data['serie']
            self.fel_numero = data['numero']
            self.fel_certificado = True
            self.fel_fecha = self.create_date

        if (self.move_type == "out_refund"):

            fel_Xml = confel.genxml(self,'NCRE')

            data = confel.firmafel(self,fel_Xml)

            if not data['resultado']:
                errores = data['descripcion_errores']
                raise ValidationError(errores[0]['mensaje_error'])

            # ET.ElementTree(fel_Xml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/" + data['uuid'] + ".xml")
            ET.ElementTree(fel_Xml).write("/opt/odoo/fel/" + data['uuid'] + ".xml",encoding="unicode")

            self.fel_uuid = data['uuid']
            self.fel_serie = data['serie']
            self.fel_numero = data['numero']
            self.fel_certificado = True
            self.fel_fecha = self.create_date


        return res


    def button_cancel(self):
        res = super(account_move, self).button_cancel()
        if (self.fel_certificado):

            fel_AnulaXml = confel.genxmlanulacion(self)

            print(ET.tostring(fel_AnulaXml))

            anula_fel = confel.anulafel(self,fel_AnulaXml)

            if not anula_fel['resultado']:
                errores = anula_fel['descripcion_errores']
                raise ValidationError(errores[0]['mensaje_error'])


        return res

    #def button_draft(self):
    #   res = super(account_move, self).button_draft()
    #    if (self.fel_certificado):
    #       raise ValidationError('Este documento esta firmado electronicamente con el numero '+self.fel_uuid+' no puede ser revertido')
    #        return res

