import frappe
from frappe.tests.utils import FrappeTestCase


class TestJobCard(FrappeTestCase):

    def test_parent_validate_runs(self):
        job = frappe.get_doc({
            "doctype": "Job Card",
            "customer_name": "Test Customer",
            "customer_phone": "123",  
            "device_type": "Laptop",
            "problem_description": "Screen issue",
            "status": "Ready for Delivery",  
            "assigned_technician": "TECH-0005"
        })

        with self.assertRaises(frappe.ValidationError):
            job.insert()