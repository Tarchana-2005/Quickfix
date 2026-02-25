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

    if any(role in user_roles for role in ["QF Manager", "System Manager", "Administrator"]):
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