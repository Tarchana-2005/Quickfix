import frappe
from frappe.utils import now

def log_change(doc, method):
    if doc.doctype == "Audit Log":
        return 
    
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doc.doctype,
        "document_name": doc.name,
        "action": method,
        "user": frappe.session.user,
        "timestamp": now()
    }).insert()

def log_login(login_manager):
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "User",
        "document_name": frappe.session.user,
        "action": "Login",
        "user": frappe.session.user,
        "timestamp": now()
    }).insert()

def log_logout(login_manager):
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "User",
        "document_name": frappe.session.user,
        "action": "Logout",
        "user": frappe.session.user,
        "timestamp": now()
    }).insert()