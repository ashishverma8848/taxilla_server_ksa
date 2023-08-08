import frappe
from datetime import datetime
import taxilla_server_ksa.taxilla_server_ksa.utils as utils
from taxilla_server_ksa.taxilla_server_ksa.item import Item
import json
class SalesInvoice():

    def __init__(self,invoice,original_invoice=None,item_list=[],vat_settings=[]):
        self.invoice = utils.to_dict_obj(invoice)
        # self.item_list = [utils.to_dict_obj(item) for item in item_list]
        # self.vat_settings = utils.to_dict_obj(vat_settings)
        # if original_invoice:
        #     self.original_invoice = utils.to_dict_obj(original_invoice)
        # self.vat_accounts = []
        # for acc in self.vat_settings.ksa_vat_sales_accounts:
        #     self.vat_accounts.append(acc.account)
        # self.generate_item_list_obj()
        



    def get_vat_rate(self):
        pass

    def generate_item_list_obj(self):
        self.item_obj_list = []
        for i in range(len(self.item_list)):
            item = Item(self.item_list[i],self.invoice.items[i],i+1,self.invoice,vat_settings=self.vat_settings)
            self.item_obj_list.append(item.item_obj())

    def tax_total_obj(self):
        self.tax_total_ob = []
        self.tax_total_ob.append({
                        "TaxAmount": {
                        "currencyID": self.invoice.currency,
                        "value": sum(i['TaxTotal']['TaxAmount']['value'] for i in self.item_obj_list)
                        },
                        "TaxSubtotal": self.tax_sub_total_obj()
                    })
        return self.tax_total_ob
    
    def legal_monetary_total(self):
        return {
                    "LineExtensionAmount": {
                        "currencyID": self.invoice.currency,
                        "value": abs(self.invoice.total)
                    },
                    "AllowanceTotalAmount": {
                        "currencyID": self.invoice.currency,
                        "value": self.invoice.discount_amount
                    },
                    "TaxExclusiveAmount": {
                        "currencyID": self.invoice.currency ,
                        "value": abs(self.invoice.net_total)
                    },
                    "TaxInclusiveAmount": {
                        "currencyID": self.invoice.currency,
                        "value": abs(self.invoice.grand_total)
                    },
                    "PrepaidAmount": {
                        "currencyID": self.invoice.currency,
                        "value": self.invoice.total_advance
                    },
                    "PayableAmount": {
                        "currencyID": self.invoice.currency,
                        "value": self.invoice.outstanding_amount
                    }
                }
        
    def tax_sub_total_obj(self):
        obj = []
        for t in self.invoice.taxes:
            if t.tax_amount and t.account_head in self.vat_accounts:
                item_tax_detail = json.loads(t.item_wise_tax_detail)
                item = list(item_tax_detail.keys())[0]
                tax_cat = ""
                for i in self.item_list:
                    if i.item_code or i.item_name == item:
                        tax_cat = i.vat_category
                        break
                obj.append({
                            "TaxableAmount": {
                            "currencyID": self.invoice.currency,
                            "value": abs(t.tax_amount*100/t.rate)
                            },
                            "TaxAmount": {
                            "currencyID": self.invoice.currency,
                            "value": abs(t.tax_amount)
                            },
                            "TaxCategory": {
                            "ID": tax_cat,
                            "Percent": t.rate,
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                            }
                        })
        return obj


    def invoice_type_code(self):
        value = "388"
        name = "0100000" # need to understand
        if self.invoice.is_return:
            value = "381"
        if self.invoice.is_debit_note:
            value = "383"
        return {
            'name': name,
            'value': value
        }

    def delivery(self):
        return  [
                    {
                        "ActualDeliveryDate": "2022-04-25", # where should I get this values
                        "LatestDeliveryDate": None # optional
                    }
                ]

    def billing_reference(self):
        if self.invoice_type_code()['value'] == "388":
            return None 
        return  [
                    {
                        "InvoiceDocumentReference": {
                        "ID": {
                            "ar": None,
                            "en": self.invoice.return_against
                        }
                        }
                    }
                ]
    
    def order_reference(self):
        return None # customer PO Number
        return {
                    "ID": {
                        "ar": None,
                        "en": "161313031"
                    }
                }
    
    def contractor_reference(self):
        return None # contract document no
        return [
                    {
                        "ID": {
                        "ar": None,
                        "en": "1771313066"
                        }
                    }
                ]