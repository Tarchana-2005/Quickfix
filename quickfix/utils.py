import frappe

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

