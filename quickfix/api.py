import frappe

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