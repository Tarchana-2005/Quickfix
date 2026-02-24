# Copyright (c) 2026, Tarchana and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
	def before_insert(self):
		if self.labour_charge is None:
			settings = frappe.db.get_single_value("QuickFix Settings", "default_labour_charge")
			self.labour_charge = settings
