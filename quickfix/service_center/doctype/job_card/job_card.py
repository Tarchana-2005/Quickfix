# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
	def before_insert(self):
		if self.labour_charge is None:
			settings = frappe.db.get_single_value("QuickFix Settings", "default_labour_charge")
			self.labour_charge = settings

	def validate(self):
		self.validate_customer_phone()
		self.technician_required()
		self.calculate_parts_used()
		self.tech_spec_mismatch_validation()

	def tech_spec_mismatch_validation(self):
		if self.assigned_technician and self.device_type:
			specialization = frappe.db.get_value(
				"Technician",
				self.assigned_technician,
				"specialization"
			)

		if specialization != self.device_type:
			frappe.msgprint("Technician specialization does not match the device type", indicator = "orange")

	def validate_customer_phone(self):
		if self.customer_phone and len(self.customer_phone) != 10:
				frappe.throw("Give a valid Phone Number")

	def technician_required(self):
		statuses = ["In Repair", "Ready for Delivery", "Delivered"]
		if self.status in statuses and not self.assigned_technician:
				frappe.throw(f"Technician must be assigned when status is {self.status}")
	
	def calculate_parts_used(self):
		parts_total = 0
		for row in self.parts_used:
			row.total_price = (row.quantity or 0) * (row.unit_price or 0)
			parts_total += row.total_price

		self.parts_total = parts_total
		self.final_amount = parts_total + (self.labour_charge or 0)
		self.amount = self.final_amount

	def before_submit(self):
		if  self.parts_used:
			for row in self.parts_used:
				stock = frappe.db.get_value("Spare Part", row.part, "stock_qty")

				if stock < row.quantity:
					frappe.throw(f"{row.part_name} has only {stock} in stock")

		if self.status != "Ready for Delivery":
			frappe.throw("Job Card can only be submitted if Ready for Delivery")

	def on_submit(self):
		for row in self.parts_used:
			current_stock = frappe.db.get_value(
				"Spare Part",
				row.part,
				"stock_qty"
			)

			new_stock = current_stock - row.quantity

			frappe.db.set_value(
				"Spare Part",
				row.part,
				"stock_qty",
				new_stock
			)

		existing_invoice = frappe.db.exists("Service Invoice", {"job_card": self.name})

		if not existing_invoice:
			frappe.get_doc({
				"doctype": "Service Invoice",
				"job_card": self.name,
				"customer_name": self.customer_name,
				"labour_charge": self.labour_charge,
				"parts_total": self.parts_total,
				"total_amount": self.final_amount,
				"payment_status": "Unpaid"
			}).insert(ignore_permissions=True)

		frappe.publish_realtime(
			event="job_ready",
			message={
				"job_card": self.name,
				"customer": self.customer_name
			},
			user = self.owner
		)
		
		frappe.enqueue(
    		"quickfix.utils.send_job_ready_email",
    		queue="short",
    		job_card=self.name
		)

		frappe.enqueue(
			"quickfix.utils.generate_monthly_revenue_report",
			year  = frappe.utils.now_datetime().year,
			queue = "long",
			timeout = 600
		)

	def on_cancel(self):
		self.status = "Cancelled"

		for row in self.parts_used:
			current_stock = frappe.db.get_value(
				"Spare Part",
				row.part,
				"stock_qty"
			)

			new_stock = current_stock + row.quantity

			frappe.db.set_value(
				"Spare Part",
				row.part,
				"stock_qty",
				new_stock
			)
		
			invoice_name = frappe.db.get_value(
				"Service Invoice",
				{"job_card": self.name},
				"name"
			)

			if invoice_name:
				invoice_doc = frappe.get_doc("Service Invoice", invoice_name)

				if invoice_doc.docstatus == 1:
					invoice_doc.cancel()

	def on_trash(self):
		if self.status not in ["Draft", "Cancelled"]:
			frappe.throw(
            	"Only Draft or Cancelled Job Cards can be deleted."
        	)
			
	def before_print(self, print_settings=None):
		self.print_summary = f"{self.customer_name} - {self.device_brand} {self.device_model}"


