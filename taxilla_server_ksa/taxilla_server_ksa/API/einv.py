import frappe 
import requests
import json 
import taxilla_server_ksa.taxilla_server_ksa.utils as utils

@frappe.whitelist(allow_guest=True)
def generate_einv(**kwargs):
    try:
        data = format_invoice(kwargs,frappe.request.headers)
        company = utils.to_dict_obj(kwargs.get('company'))
        return einv_request(data,frappe.request.headers)
    except Exception as e:
        frappe.logger('taxilla').exception(e)
        return utils.error_response(e)

def format_invoice(kwargs,header_data):
    try:
        invoice = kwargs.get('invoice')
        frappe.log_error("inovice",invoice)
        return {
                "ReferenceNumber": invoice.get('name'),
                # "FinancialYear": invoice.get('posting_date'),
                # "InvTypeCd": "388",
                }

    except Exception as e:
        frappe.logger('taxilla').exception(e)
        return utils.error_response(e)

def einv_request(data,header_data):
    frappe.log_error("final",data)
    try:
        # base_url = "https://api-sandbox.taxilla.com"
        # if header_data.get('Sandbox') == '0':
        base_url = "https://ksa.taxilla.com/" 
        url = "https://ksa.taxilla.com/process/v1/einvoicearksa?autoExecuteRules=true&transformationName=KSA-eInvoice-Json-Inbound"
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 41c7ec0e-0652-4f81-9705-942a752bc3c2'
        }
        payload = json.dumps(data, indent=4, sort_keys=False, default=str)
        frappe.msgprint(str(payload))
        response = requests.request("POST",url,headers=headers,data=payload)
        response = response.json()
        frappe.log_error("response",response)

        msg = 'Failed'
        if response.get('Status') == 'GENERATED':
            msg = 'Success'
        return {'msg':msg,'response':response, 'request':payload}
    except Exception as e:
        frappe.logger('taxilla').exception(e)
        return utils.error_response(e)