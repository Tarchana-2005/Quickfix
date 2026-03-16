# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Technician(Document):
	def validate(self):
		if self.email:
			if frappe.db.exists("User", self.email):
				frappe.throw("The email is already exist")

	def after_insert(self):
		self.create_login_user()

	def create_login_user(self):
		email = self.email

		if not email:
			frappe.throw("Email is required to create login account")

		if frappe.db.exists("User", email):
			return
		
		user = frappe.get_doc({
			"doctype": "User",
			"email": self.email,
			"first_name": self.technician_name,
			"enabled": 1,

			"send_welcome_email": 1,

			"roles": [
				{"role": "QF Technician"}
			]
		})

		user.insert()
		self.db_set("user", email)


