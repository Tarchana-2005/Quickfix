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

    import frappe

def rename_technician(old_name, new_name):
    frappe.rename_doc(
        "Technician",
        old_name,
        new_name,
        merge=False
    )

    # merge=True is dangerous because it deletes the old record 
    # and merges all links into existing one, which can lead to accidental data loss