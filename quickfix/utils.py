import frappe
from frappe.utils import today

def send_job_ready_email(job_card):

    doc = frappe.get_doc("Job Card", job_card)

    if not doc.customer_email:
        return

    frappe.sendmail(
        recipients=doc.customer_email,
        subject=f"Your Repair is Ready - {doc.name}",
        message=f"""
        Dear {doc.customer_name},

        Your device repair (Job Card: {doc.name}) is ready for delivery.

        Final Amount: ₹{doc.final_amount}

        Thank you,
        QuickFix Service Centre
        """
    )

def generate_monthly_revenue_report(year):
    """
    Long running background job that generates revenue report
    """

    months = range(1, 13)

    for i, month in enumerate(months, 1):

        total = frappe.db.sql("""
            SELECT SUM(final_amount)
            FROM `tabJob Card`
            WHERE YEAR(creation)=%s AND MONTH(creation)=%s
        """, (year, month))[0][0]

        frappe.publish_progress(
            percent=round(i / 12 * 100),
            title="Generating Revenue Report",
            description=f"Processing month {month}"
        )

    frappe.logger().info("Monthly revenue report generated")

def rename_technician(old_name, new_name):
    frappe.rename_doc(
        "Technician",
        old_name,
        new_name,
        merge=False
    )

    # merge=True is dangerous because it deletes the old record 
    # and merges all links into existing one, which can lead to accidental data loss

def get_shop_name():
    settings = frappe.get_single("QuickFix Settings")
    return settings.shop_name

def format_job_id(value):
    return f"JOB#{value}"

def check_low_stock():
    last_run = frappe.db.get_value(
        "Audit Log",
        {"action": "low_stock_check", "date": today()},
        "name"
    )
    if last_run:
        return  

    frappe.get_doc({
        "doctype": "Audit Log",
        "action": "low_stock_check",
        "date": today(),
        "user": "Administrator",
        "doctype_name": "Spare Part",
        "document_name": "daily_check",
        "timestamp": frappe.utils.now()
    }).insert(ignore_permissions=True)

    frappe.db.commit()

@frappe.whitelist()
def deliberately_failing_job():
    raise Exception("Deliberate failure")

# def n_plus_one_issue():
#     job_cards = frappe.get_all(
#         "Job Card",
#         fields=["name", "assigned_technician"]
#     )
#     for jc in job_cards:
#         if jc.assigned_technician:
#             tech = frappe.get_doc("Technician", jc.assigned_technician)
#             print(tech.technician_name, tech.phone)

# def n_plus_one_fixed():
#     job_cards = frappe.get_all(
#         "Job Card",
#         fields=[
#             "name",
#             "assigned_technician",
#             "assigned_technician.technician_name",
#             "assigned_technician.phone"
#         ]
#     )
#     for jc in job_cards:
#         print(jc.get("technician_name"), jc.get("phone"))

def n_plus_one_fixed():
    job_cards = frappe.get_all(
        "Job Card",
        fields=[
            "name",
            "assigned_technician",
            "assigned_technician.technician_name",
            "assigned_technician.phone"
        ]
    )

    seen = set()
    for jc in job_cards:
        tech = jc.get("assigned_technician")
        if not tech or tech in seen:
            continue

        print(jc.get("technician_name"), jc.get("phone"))

        seen.add(tech)

import time

def bulk_operations_demo():
    start = time.time()

    frappe.db.sql("""
        UPDATE `tabJob Card`
        SET status = 'Cancelled'
        WHERE status = 'Draft'
    """)
    frappe.db.commit()

    end = time.time()
    print(f"SQL UPDATE took: {end - start} seconds")

    start = time.time()

    values = []
    for i in range(50):
        values.append({
            "name": f"BULK-TEST-{i}",
            "action": "bulk_test",
            "user": "Administrator",
            "doctype_name": "Job Card",
            "document_name": f"test-{i}",
            "timestamp": frappe.utils.now(),
            "date": frappe.utils.today()
        })

    frappe.db.bulk_insert(
        "Audit Log",
        fields=["name", "action", "user", 
                "doctype_name", "document_name", 
                "timestamp", "date"],
        values=[[v["name"], v["action"], v["user"],
                 v["doctype_name"], v["document_name"],
                 v["timestamp"], v["date"]] for v in values]
    )
    frappe.db.commit()

    end = time.time()
    print(f"bulk_insert took: {end - start} seconds")

