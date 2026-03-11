import frappe
from frappe.utils import now
from frappe.client import get_count

@frappe.whitelist()
def share_job_card(job_card_name, user_email):
    frappe.only_for("QF Manager")

    if not frappe.db.exists("Job Card", job_card_name):
        frappe.throw("Job Card not found")

    if not frappe.db.exists("User", user_email):
        frappe.throw("USer not found")

    frappe.share.add(
        "Job Card",
        job_card_name,
        user_email,
        read=1
    )

    return f"Job Card {job_card_name} shared with {user_email}"

@frappe.whitelist()
def get_job_cards_unsafe():
    return frappe.get_all("Job Card", fields="*")

@frappe.whitelist()
def get_job_cards_safe():

    user = frappe.session.user
    roles = frappe.get_roles(user)

    job_cards = frappe.get_list(
        "Job Card",
        fields=["name", "customer_name", "customer_phone", "customer_email", "status"]
    )

    if "QF Manager" not in roles:
        for jc in job_cards:
            jc.pop("customer_phone", None)
            jc.pop("customer_email", None)

    return job_cards

@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
 
    frappe.get_doc({
        "doctype":"Audit Log",
        "doctype_name":doctype,
        "document_name": "Count Request",
        "action":"count_queried",
        "user":frappe.session.user,
        "timestamp": now()
        }).insert(ignore_permissions=True)
    frappe.db.commit()
    
    return get_count(doctype, filters, debug, cache)

@frappe.whitelist()
def transfer_job(job_card, new_technician):

    doc = frappe.get_doc("Job Card", job_card)

    doc.assigned_technician = new_technician

    doc.save()

    return "success"

@frappe.whitelist()
def generate_technician_performance_report(filters=None):
    """
    Trigger prepared report generation in background
    """

    frappe.enqueue(
        method="frappe.desk.query_report.run",
        queue="long",
        report_name="Technician Performance Report",
        filters=filters or {}
    )

    return "Prepared report generation started"
