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
    frappe.enqueue(
        method="frappe.desk.query_report.run",
        queue="long",
        report_name="Technician Performance Report",
        filters=filters or {}
    )

    return "Prepared report generation started"

@frappe.whitelist()
def get_job_summary():
    job_card_name = frappe.form_dict.get("job_card_name")

    if not job_card_name:
        frappe.response.http_status_code = 400
        return {"error": "job_card_name is required"}

    if not frappe.db.exists("Job Card", job_card_name):
        frappe.response.http_status_code = 404
        return {"error": "Not found"}

    doc = frappe.get_doc("Job Card", job_card_name)

    return {
        "name": doc.name,
        "status": doc.status,
        "device_type": doc.device_type,
        "device_brand": doc.device_brand,
        "device_model": doc.device_model,
        "assigned_technician": doc.assigned_technician,
        "priority": doc.priority,
        "final_amount": float(doc.final_amount or 0),
        "parts_total": float(doc.parts_total or 0),
        "diagnosis_date": doc.diagnosis_date,  
        "payment_status": doc.payment_status,
    }

@frappe.whitelist(allow_guest=True)
def get_job_by_phone():
    ip = frappe.local.request_ip
    cache_key = f"rate_limit:{ip}"
    count = frappe.cache.get_value(cache_key) or 0

    if int(count) >= 10:
        frappe.response.http_status_code = 429
        return {"error": "Too many requests. Wait a minute."}

    frappe.cache.set_value(cache_key, int(count) + 1, expires_in_sec=60)
    
    return {"message": "Request allowed", "call_count": int(count) + 1}

def send_webhook(job_card_name):
    import requests, json
    settings = frappe.get_single("QuickFix Settings")
    if not settings.webhook_url:
        return
    doc = frappe.get_doc("Job Card", job_card_name)

    payload = {"event":"job_submitted","job_card":doc.name,"amount":doc.final_amount}
    try:
        r = requests.post(settings.webhook_url, json=payload, timeout=5)
        r.raise_for_status()
    except Exception as e:
        frappe.log_error(f"Webhook failed: {e}", "Webhook Error")

@frappe.whitelist(allow_guest=True)
def payment_webhook():
    import hmac
    import hashlib
    import json

    payload = frappe.request.data

    secret = frappe.conf.get("payment_webhook_secret", "")
    signature = frappe.get_request_header("X-Signature")
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature or ""):
        frappe.throw("Invalid signature", frappe.AuthenticationError)

    data = json.loads(payload)

    if frappe.db.exists("Audit Log", {
        "action": "payment_received",
        "document_name": data.get("ref")
    }):
        return {
            "status": "duplicate",
            "message": "Already processed"
        }

    job_card_name = data.get("job_card")
    if job_card_name and frappe.db.exists("Job Card", job_card_name):
        frappe.db.set_value(
            "Job Card",
            job_card_name,
            "payment_status",
            "Paid"
        )

    invoice_name = frappe.db.get_value(
        "Service Invoice",
        {"job_card": job_card_name},
        "name"
    )
    if invoice_name:
        frappe.db.set_value(
            "Service Invoice",
            invoice_name,
            "payment_status",
            "Paid"
        )

    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": "Job Card",
        "document_name": data.get("ref"),
        "action": "payment_received",
        "user": "Administrator",
        "timestamp": frappe.utils.now()
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return {"status": "ok"}