import frappe

def technician_permission(user):

    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if any(role in user_roles for role in ["QF Manager", "System Manager", "Administrator"]):
        return ""

    if "QF Technician" in user_roles:
        return f"""(`tabTechnician`.user = {frappe.db.escape(user)})"""

    return "1=0"


def job_card_permission(user):

    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if any(role in user_roles for role in ["QF Manager", "System Manager", "Administrator", "QF Service Staff"]):
        return ""

    if "QF Technician" in user_roles:

        technician = frappe.db.get_value(
            "Technician",
            {"user": user},
            "name"
        )

        if not technician:
            return "1=0"

        return f"""(`tabJob Card`.assigned_technician = {frappe.db.escape(technician)})"""

    return "1=0"


def service_invoice_has_permission(doc, user=None, ptype=None, debug=False):

    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)

    if "QF Manager" in roles or "System Manager" in roles or "Administrator" in roles:
        return True

    if ptype == "read":

        if not doc.job_card:
            return False

        payment_status = frappe.db.get_value(
            "Job Card",      
            doc.job_card,
            "payment_status"
        )

        if payment_status == "Paid":
            return True
        else:
            return False

    return True