import frappe

def before_uninstall():
    submitted = frappe.db.exists(
        "Job Card",
        {"docstatus": 1}
    )

    if submitted:
        frappe.throw("Cannot uninstall QuickFix because submitted Job Cards exists.", frappe.ValidationError)