# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ServiceInvoice(Document):
	def on_submit(self):
		invoice_status = self.payment_status
		
		frappe.db.set_value(
    		"Job Card",
    		self.job_card,
    		"payment_status",
    		invoice_status
		)
