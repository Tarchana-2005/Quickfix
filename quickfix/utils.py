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