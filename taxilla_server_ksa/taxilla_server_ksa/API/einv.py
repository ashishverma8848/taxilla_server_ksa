import frappe 
import requests
import json 
import taxilla_server_ksa.taxilla_server_ksa.utils as utils
from taxilla_server_ksa.taxilla_server_ksa.sales_invoice import SalesInvoice
from taxilla_server_ksa.taxilla_server_ksa.address import Address

@frappe.whitelist(allow_guest=True)
def generate_einv(**kwargs):
    try:
        data = format_invoice(kwargs,frappe.request.headers)
        company = utils.to_dict_obj(kwargs.get('company'))
        return einv_request(data,frappe.request.headers,company.tax_id)
    except Exception as e:
        frappe.logger('taxilla').exception(e)
        return utils.error_response(e)

def format_invoice(kwargs,header_data):
    try:
        invoice = utils.to_dict_obj(kwargs.get('invoice'))
        invoice_obj = SalesInvoice(kwargs.get('invoice'),item_list = kwargs.get('item_list'),vat_settings=kwargs.get('vat_settings'))
        supplier_address = Address(kwargs.get('company_address'),company = kwargs.get('company'),company_name=invoice.company)
        customer_addresss = Address(kwargs.get('customer_address'),customer=kwargs.get('customer'))
        return {
                "DeviceId": header_data.get('device'),
                "EInvoice": {
                    "ProfileID": "reporting:1.0",
                    "ID": {
                    "en": invoice.name,
                    "ar": None
                    },
                    "InvoiceTypeCode": invoice_obj.invoice_type_code(),
                    "IssueDate": invoice.posting_date,
                    "IssueTime": "15:30:00",
                    "Delivery":invoice_obj.delivery(),
                    "BillingReference":invoice_obj.billing_reference(),
                    "OrderReference": invoice_obj.order_reference(),
                    "ContractDocumentReference": invoice_obj.contractor_reference(),
                    "DocumentCurrencyCode": invoice.currency,
                    "TaxCurrencyCode": "SAR", #need to check
                    "AccountingSupplierParty": supplier_address.address_object(),
                    "AccountingCustomerParty": customer_addresss.address_object(),
                    "InvoiceLine": invoice_obj.item_obj_list,
                    "TaxTotal": invoice_obj.tax_total_obj(),
                    "LegalMonetaryTotal": invoice_obj.legal_monetary_total(),
                    "PaymentMeans": [
                    {
                        "PaymentMeansCode": "42",
                        "InstructionNote": {
                        "en": "10",
                        "ar": ""
                        },
                        "PayeeFinancialAccount": {
                        "PaymentNote": {
                            "en": "",
                            "ar": ""
                        }
                        }
                    }
                    ],
                    "Note": {
                    "en": "This is a computer generated invoice.",
                    "ar": None
                    }
                },
                "CustomFields": {
                    "TotalBoxes": "2",
                    "TotalWreight": "36"
                }
                }
    except Exception as e:
        frappe.logger('taxilla').exception(e)
        return utils.error_response(e)

def einv_request(data,header_data,vat):
    try:
        base_url = "https://api-sandbox.taxilla.com"
        if header_data.get('Sandbox') == '0':
            base_url = "https://ksa.taxilla.com/" 
        url = base_url + "process/v1/einvoicearksa?autoExecuteRules=true&transformationName=KSA-eInvoice-Json-Inbound"
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer c772a4d9-3cf5-4932-898d-055ec8506c66'
        }
        payload = json.dumps(data, indent=4, sort_keys=False, default=str)
        response = requests.request("POST",url,headers=headers,data=payload)
        response = response.json()
        msg = 'Failed'
        if response.get('Status') == 'GENERATED':
            msg = 'Success'
        return {'msg':msg,'response':response, 'request':payload}
    except Exception as e:
        frappe.logger('taxilla').exception(e)
        return utils.error_response(e)