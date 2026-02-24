# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class SparePart(Document):
	def autoname(self):
		self.name = self.part_code.upper() + "-" + make_autoname("PART-.YYYY.-.####")

	def validate(self):
		if self.selling_price is not None and self.unit_cost is not None:
			if self.selling_price <= self.unit_cost:
				frappe.throw("Selling price must be greater than Unit cost")
