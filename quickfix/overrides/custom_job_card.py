import frappe
from quickfix.service_center.doctype.job_card.job_card import JobCard
class CustomJobCard(JobCard):
    def validate(self):
        super().validate() 
        self._check_urgent_unassigned()

    def _check_urgent_unassigned(self):
        if self.priority == "Urgent" and not self.assigned_technician:
            settings = frappe.get_single("QuickFix Settings")
            frappe.enqueue("quickfix.utils.send_urgent_alert",
            job_card=self.name, manager=settings.manager_email)

"""
Method Resolution Order (MRO):

MRO is the order in which Python looks for a method when a class
inherits from another class. Since CustomJobCard extends JobCard,
Python first checks for methods in CustomJobCard. If not found,
it then checks JobCard and its parent class Document.

Calling super() is mandatory.
Even though CustomJobCard inherits from JobCard (which inherits from 
Document in Frappe core), if we override a method and don't call super(), 
the execution will not reach the parent implementation. So any core updates 
inside the parent method will not run.
"""
