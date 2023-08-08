import frappe
import json
class Item():

    def __init__(self,item,row,id,invoice,vat_settings=None):
        self.item = item
        self.row = row 
        self.id = id
        self.invoice = invoice
        self.round_off = 0
        self.discount = abs(row.discount_amount) if row.discount_amount>0 else 0
        if not vat_settings:
            frappe.throw('Please Configure KSA VAT Settings for your company!')
        self.vat_accounts = []
        for acc in vat_settings.ksa_vat_sales_accounts:
            self.vat_accounts.append(acc.account)
        self.tax_details()
        
        


    def tax_details(self):
        for t in self.invoice.taxes:
            if t.tax_amount and t.account_head in self.vat_accounts:
                item_tax_detail = json.loads(t.item_wise_tax_detail).get(self.item.item_code or self.item.item_name)
                self.item_tax_rate = "{:.2f}".format(item_tax_detail[0])
                self.item_tax_amount = (float(self.item_tax_rate) / 100) * self.row.amount
                self.round_off = round(abs(self.row.amount) + abs(self.item_tax_amount))

    def item_obj(self):
        return {
                        "ID": self.id,
                        "Item": {
                        "Name": {
                            "en": self.item.item_name,
                            "ar": None
                        },
                        "BuyersItemIdentification": None,       
                        "SellersItemIdentification": {
                            "ID": {
                            "en": self.item.item_code,
                            "ar": None
                            }
                        },
                        "StandardItemIdentification":None,
                        "ClassifiedTaxCategory": {
                            "ID": self.item.vat_category,
                            "Percent": self.item_tax_rate,
                            "TaxScheme": {
                            "ID": "VAT"
                            }
                        }
                        },
                        "Price": {
                        "AllowanceCharge": {
                            "ChargeIndicator": "false",
                            "BaseAmount": {
                            "currencyID": self.invoice.currency,
                            "value": abs(self.row.amount) + abs(self.discount)
                            },
                            "Amount": {
                            "currencyID": self.invoice.currency,
                            "value": abs(self.discount)
                            }
                        },
                        "PriceAmount": {
                            "currencyID": self.invoice.currency,
                            "value": abs(self.row.amount)
                        },
                        "BaseQuantity": {
                            "unitCode": None, #need to map later
                            "value": abs(self.row.qty)
                        }
                        },
                        "InvoicedQuantity": {
                        "unitCode": None, #need to map later optional
                        "value": abs(self.row.qty)
                        },
                        "AllowanceCharge":[], #need logic for additional discount(Invoice Level) optional
                        "LineExtensionAmount": {
                        "currencyID": self.invoice.currency,
                        "value": abs(self.row.amount)
                        },
                        "TaxTotal": {
                        "TaxAmount": {
                            "currencyID": self.invoice.currency,
                            "value": abs(self.item_tax_amount)
                        },
                        "RoundingAmount": {
                            "currencyID": self.invoice.currency,
                            "value": self.round_off
                        }
                        }
                    }