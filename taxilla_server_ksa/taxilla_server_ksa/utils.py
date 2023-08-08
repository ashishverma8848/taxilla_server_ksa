import frappe
from frappe import *
import json

class obj:
    def __init__(self, dict1):
        self.__dict__.update(dict1)


def get_dict(type,doc):
    if frappe.db.exists(type,doc):
        return frappe.get_doc(type,doc).as_dict()
    return None

def get_object(raw_dict):
    return json.loads(json.dumps(raw_dict),object_hook=obj)

def success_response(data=None):
    response = {'msg': 'success'}
    if data: 
        response['data'] = data
    return response 

def error_response(err_msg):
    return {
        'msg': 'error',
        'error': err_msg
    }

def response_error_handling(response):
    error = ""
    errors = []
    if type(response) == list:
        response = response[0]
    if type(response) == str:
        return error_response(response)
    if type(response) == None:
        return error_response("No response received!")
    if response.get('govt_response'):
        if response.get('govt_response').get('ErrorDetails'):
            errors = response.get('govt_response').get('ErrorDetails')
    elif response.get('ErrorDetails'):
        errors = response.get('ErrorDetails')
    elif response.get('errorDetails'):
        errors.append(response.get('errorDetails'))
    elif response.get('errors'):
        if response.get('errors').get('errors'):
            errors = response.get('errors').get('errors')
    else:
        errors.append({'error_message':json.dumps(response)})
    c=1
    for i in errors:
        error += str(c) + ". " + i.get("error_message") + "\r\n"
        c+=1 
    return error_response(error)



        
def response_logger(payload,response,api,doc_type,doc_name,status="Failed"):
    try:
        return
        response = json.dumps(response, indent=4, sort_keys=False, default=str)
        if frappe.db.exists('Taxilla API Log',{'document_name':doc_name,'api':api}):
            doc = frappe.get_doc('Taxilla API Log',{'document_name':doc_name,'api':api})
            doc.request_data = payload
            doc.response = response
            doc.status = status
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.new_doc('Taxilla API Log')
            doc.document_type = doc_type
            doc.document_name = doc_name
            doc.api = api
            doc.request_data = payload
            doc.response = response
            doc.status = status
            doc.insert(ignore_permissions=True)
    except Exception as e:
        frappe.logger('response').exception(e)

class DictObj:
    def __init__(self, in_dict:dict):
        pass
        # for key, val in in_dict.items():
        #     if isinstance(val, (list, tuple)):
        #        setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
        #     else:
        #        setattr(self, key, DictObj(val) if isinstance(val, dict) else val)
               

def to_dict_obj(raw_dict):
    return DictObj(raw_dict)


def map_uom(uom):
    if uom == 'Kg':
        return 'KGS'
    elif uom == 'Box':
        return 'BOX'
    elif uom == 'Cubic Meter':
        return 'CBM'
    elif uom == 'Cubic Centimeter':
        return 'CCM'
    elif uom == 'Centimeter':
        return 'CMS'
    elif uom == 'Kilometer':
        return 'KME'
    elif uom == 'Meter':
        return 'MTR'
    elif uom == 'Millilitre':
        return 'MLT'
    elif uom == 'Nos' or 'NOS':
        return 'NOS'
    elif uom == 'Roll':
        return 'ROL'
    elif uom == 'Set':
        return 'SET'
    elif uom == 'Square Meter':
        return 'SQM'
    elif uom == 'Square Yard':
        return 'SQY'
    elif uom == 'Square Yard':
        return 'SQF'
    elif uom == 'Unit':
        return 'UNT'
    elif uom == 'Yard':
        return 'YDS'
    return 'OTH'