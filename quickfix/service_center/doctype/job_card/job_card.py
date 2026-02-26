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

	def before_submit(self):
		if  self.parts_used:
			for row in self.parts_used:
				stock = frappe.db.get_value("Spare Part", row.part, "stock_qty")

				if stock < row.quantity:
					frappe.throw(f"{row.part_name} has only {stock} in stock")

		if self.status != "Ready for Delivery":
			frappe.throw("Job Card can only be submitted if Ready for Delivery")

	def on_submit(self):
		frappe.get_doc({
			"doctype": "Service Invoice",
			"job_card": self.name,
			"customer_name": self.customer_name,
			"labour_charge": self.labour_charge,
			"parts_total": self.parts_total,
			"total_amount": self.final_amount,
			"payment_status": self.payment_status
		}).insert()

		
		



